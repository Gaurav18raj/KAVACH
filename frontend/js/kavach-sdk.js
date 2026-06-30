/**
 * KAVACH - Behavioral Collector SDK (Mock)
 * Captures keystroke dynamics, navigation timing, and device fingerprint.
 */

class KavachSDK {
    constructor() {
        this.sessionData = {
            keystrokes: {
                holdDurations: [],
                ikiValues: [],
                backspaceCount: 0,
                hesitationMs: 0
            },
            haptics: {
                mouseEntropy: 0,
                clickPatterns: []
            },
            device: this.getDeviceFingerprint()
        };

        this.lastKeyDownTime = null;
        this.lastKeyUpTime = null;
        this.formStartTime = Date.now();
        this.demoMode = 'normal'; // Can be 'normal' or 'jamtara'
        
        this.initListeners();
    }

    getDeviceFingerprint() {
        // Generate and cache canvas fingerprint
        let canvasHash = localStorage.getItem('kavach_canvas_hash');
        if (!canvasHash) {
            canvasHash = this.generateCanvasFingerprint();
            localStorage.setItem('kavach_canvas_hash', canvasHash);
        }

        return {
            userAgent: navigator.userAgent,
            screenRes: `${window.screen.width}x${window.screen.height}`,
            timezoneOffset: new Date().getTimezoneOffset(),
            language: navigator.language,
            canvasHash: canvasHash
        };
    }

    generateCanvasFingerprint() {
        try {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            ctx.textBaseline = "top";
            ctx.font = "14px 'Arial'";
            ctx.textBaseline = "alphabetic";
            ctx.fillStyle = "#f60";
            ctx.fillRect(125,1,62,20);
            ctx.fillStyle = "#069";
            ctx.fillText("KavachFingerprint2024", 2, 15);
            ctx.fillStyle = "rgba(102, 204, 0, 0.7)";
            ctx.fillText("KavachFingerprint2024", 4, 17);
            
            const dataUrl = canvas.toDataURL();
            
            // Simple djb2 hash
            let hash = 5381;
            for (let i = 0; i < dataUrl.length; i++) {
                hash = ((hash << 5) + hash) + dataUrl.charCodeAt(i);
            }
            return "kavach_" + Math.abs(hash).toString(16);
        } catch (e) {
            return "kavach_fallback_hash";
        }
    }

    initListeners() {
        // Track keystrokes
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace') {
                this.sessionData.keystrokes.backspaceCount++;
            }
            this.lastKeyDownTime = Date.now();
            
            if (this.lastKeyUpTime) {
                const iki = this.lastKeyDownTime - this.lastKeyUpTime;
                if (iki > 0 && iki < 2000) { // filter out massive gaps
                    this.sessionData.keystrokes.ikiValues.push(iki);
                }
            }
        });

        document.addEventListener('keyup', (e) => {
            const upTime = Date.now();
            let currentHold = 0;
            let currentIki = 0;

            if (this.lastKeyDownTime) {
                currentHold = upTime - this.lastKeyDownTime;
                if (currentHold > 0 && currentHold < 1000) { // filter outliers
                    this.sessionData.keystrokes.holdDurations.push(currentHold);
                }
            }

            if (this.lastKeyUpTime && this.lastKeyDownTime) {
                currentIki = this.lastKeyDownTime - this.lastKeyUpTime;
            }

            this.lastKeyUpTime = upTime;

            // Dispatch Live Telemetry Event for UI Visualization
            const event = new CustomEvent('kavach_keystroke', {
                detail: {
                    key: e.key,
                    hold: currentHold,
                    iki: currentIki > 0 && currentIki < 2000 ? currentIki : 0,
                    mouseEntropy: this.sessionData.haptics.mouseEntropy
                }
            });
            window.dispatchEvent(event);
        });

        // Track hesitation on form submit
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', () => {
                if (this.lastKeyUpTime) {
                    this.sessionData.keystrokes.hesitationMs = Date.now() - this.lastKeyUpTime;
                }
            });
        });

        // Advanced Sensor Fusion: True Mouse Entropy Calculation (Variance/Jerkiness)
        this.lastMouseX = -1;
        this.lastMouseY = -1;
        this.lastMouseTime = -1;
        document.addEventListener('mousemove', (e) => {
            const now = Date.now();
            if (this.lastMouseX !== -1 && this.lastMouseTime !== -1) {
                const distance = Math.sqrt(Math.pow(e.clientX - this.lastMouseX, 2) + Math.pow(e.clientY - this.lastMouseY, 2));
                const timeDiff = now - this.lastMouseTime;
                
                // Track rapid, jerky movements typical of Remote Desktop latency
                if (timeDiff > 0 && distance > 0) {
                    const speed = distance / timeDiff;
                    if (speed > 5.0) { // Highly erratic speed jump
                        this.sessionData.haptics.mouseEntropy += speed;
                    }
                }
            }
            this.lastMouseX = e.clientX;
            this.lastMouseY = e.clientY;
            this.lastMouseTime = now;
        });

        // Advanced Sensor Fusion: Gyroscope (Device Haptics)
        this.sessionData.haptics.gyroAngle = 0.0;
        window.addEventListener('deviceorientation', (e) => {
            if (e.beta !== null) {
                this.sessionData.haptics.gyroAngle = e.beta; // Tilt front-to-back
            }
        });
    }

    // Used for Hackathon Web UI demonstration
    setDemoMode(mode) {
        this.demoMode = mode;
        console.log(`[KAVACH SDK] Demo mode set to: ${mode}`);
    }

    // Call this before sending API requests
    getPayload(transactionAmount = 0.0) {
        if (this.demoMode === 'jamtara') {
            return {
                timestamp: Date.now(),
                behavioral_data: {
                    hold_mean: 250.0,
                    hold_std: 150.0, // Erratic, slow typing (hunting for keys)
                    iki_mean: 500.0,
                    iki_std: 300.0,
                    backspace_count: 5,
                    hesitation_ms: 2500.0,
                    mouse_entropy: 450.0, // High AnyDesk Network Latency Jerks
                    gyro_angle: 0.001,    // Phone lying perfectly flat on desk
                    gyro_available: true,
                    transaction_amount: transactionAmount
                },
                device: {
                    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 AnyDesk",
                    screenRes: "1920x1080",
                    timezoneOffset: -330,
                    language: "en-US",
                    canvasHash: "hacker_canvas_hash" // Unrecognized Device
                }
            };
        }

        const hasGyro = this.sessionData.haptics.gyroAngle !== 0.0;
        const finalGyro = this.sessionData.haptics.gyroAngle;

        return {
            timestamp: Date.now(),
            behavioral_data: {
                hold_mean: this.calculateMean(this.sessionData.keystrokes.holdDurations),
                hold_std: this.calculateStd(this.sessionData.keystrokes.holdDurations),
                iki_mean: this.calculateMean(this.sessionData.keystrokes.ikiValues),
                iki_std: this.calculateStd(this.sessionData.keystrokes.ikiValues),
                backspace_count: this.sessionData.keystrokes.backspaceCount,
                hesitation_ms: this.sessionData.keystrokes.hesitationMs,
                mouse_entropy: parseFloat(this.sessionData.haptics.mouseEntropy.toFixed(2)),
                gyro_angle: parseFloat(finalGyro.toFixed(3)),
                gyro_available: hasGyro,
                transaction_amount: transactionAmount
            },
            device: this.sessionData.device
        };
    }

    calculateMean(arr) {
        if (!arr || arr.length === 0) return 0;
        const sum = arr.reduce((a, b) => a + b, 0);
        return Math.round(sum / arr.length);
    }

    calculateStd(arr) {
        if (!arr || arr.length === 0) return 0;
        const mean = this.calculateMean(arr);
        const sqDiffs = arr.map(value => Math.pow(value - mean, 2));
        const avgSqDiff = this.calculateMean(sqDiffs);
        return Math.round(Math.sqrt(avgSqDiff));
    }
}

// Initialize globally
window.Kavach = new KavachSDK();
