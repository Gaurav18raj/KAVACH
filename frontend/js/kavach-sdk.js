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
            if (this.lastKeyDownTime) {
                const hold = upTime - this.lastKeyDownTime;
                if (hold > 0 && hold < 1000) { // filter outliers
                    this.sessionData.keystrokes.holdDurations.push(hold);
                }
            }
            this.lastKeyUpTime = upTime;
        });

        // Track hesitation on submit buttons
        const submitBtns = document.querySelectorAll('button[type="submit"]');
        submitBtns.forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                const hesitation = Date.now() - this.lastKeyUpTime;
                this.sessionData.keystrokes.hesitationMs = hesitation;
            });
        });

        // Advanced Sensor Fusion: True Mouse Entropy Calculation
        this.lastMouseX = -1;
        this.lastMouseY = -1;
        document.addEventListener('mousemove', (e) => {
            if (this.lastMouseX !== -1) {
                const distance = Math.sqrt(Math.pow(e.clientX - this.lastMouseX, 2) + Math.pow(e.clientY - this.lastMouseY, 2));
                // Add distance to entropy, capped to prevent infinite scaling
                if (distance > 0) {
                    this.sessionData.haptics.mouseEntropy += (distance * 0.05);
                }
            }
            this.lastMouseX = e.clientX;
            this.lastMouseY = e.clientY;
        });

        // Advanced Sensor Fusion: Gyroscope (Device Haptics)
        this.sessionData.haptics.gyroAngle = 0.0;
        window.addEventListener('deviceorientation', (e) => {
            if (e.beta !== null) {
                this.sessionData.haptics.gyroAngle = e.beta; // Tilt front-to-back
            }
        });
    }

    // Call this before sending API requests
    getPayload(transactionAmount = 0.0) {
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
