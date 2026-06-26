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
        // Mock fingerprinting
        return {
            userAgent: navigator.userAgent,
            screenRes: `${window.screen.width}x${window.screen.height}`,
            timezoneOffset: new Date().getTimezoneOffset(),
            language: navigator.language,
            canvasHash: "mock_canvas_hash_" + Math.floor(Math.random() * 1000)
        };
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
        // For the Hackathon Demo, if running on Desktop where gyro doesn't exist, we send 0.001 to mock a flat device
        let finalGyro = this.sessionData.haptics.gyroAngle;
        if (finalGyro === 0.0) {
             finalGyro = 0.001; 
        }

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
