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

        // Mock Mouse Entropy (simplified for demo)
        document.addEventListener('mousemove', (e) => {
            // Simplified calculation just to show data collection
            this.sessionData.haptics.mouseEntropy += 0.01; 
        });
    }

    // Call this before sending API requests
    getPayload() {
        return {
            timestamp: Date.now(),
            behavioral_data: {
                hold_mean: this.calculateMean(this.sessionData.keystrokes.holdDurations),
                hold_std: this.calculateStd(this.sessionData.keystrokes.holdDurations),
                iki_mean: this.calculateMean(this.sessionData.keystrokes.ikiValues),
                iki_std: this.calculateStd(this.sessionData.keystrokes.ikiValues),
                backspace_count: this.sessionData.keystrokes.backspaceCount,
                hesitation_ms: this.sessionData.keystrokes.hesitationMs,
                mouse_entropy: parseFloat(this.sessionData.haptics.mouseEntropy.toFixed(2))
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
