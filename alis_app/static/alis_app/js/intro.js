(() => {
  const $ = (sel, root = document) => root.querySelector(sel);

  const data = $("#introData");
  const NEXT_URL = data?.dataset?.nextUrl || "/showcase/";
  const INTRO_SEEN_KEY = data?.dataset?.introSeenKey || "alis_intro_movie_seen_v6";

  const skipBtn = $("#skipIntro");
  const initBtn = $("#initIntel");
  const cta = $(".intro-cta");
  const progressFill = $("#progressFill");
  const caption = $("#caption");

  // SVG Groups
  const s1 = $("#scene1");
  const s2 = $("#scene2");
  const s3 = $("#scene3");
  const s4 = $("#scene4");
  const s5 = $("#scene5");
  const s6 = $("#scene6");
  const s8 = $("#scene8");
  const s9 = $("#scene9");

  // Specific elements for animation
  const holoRing = $("#holoRing");
  const scanPulse = $("#scanPulse");
  const activeRoadmap = $("#activeRoadmap");
  const checkSuccess = $("#checkSuccess");
  const strengthCard = $("#strengthCard");
  const weaknessCard = $("#weaknessCard");

  // --- PREMIUM CINEMATIC WEB AUDIO SYSTEM ---
  class ALISAudioSystem {
    constructor() {
      this.ctx = null;
      this.mainGain = null;
      this.filter = null;
      this.isStarted = false;
      this.intervals = [];
    }

    init() {
      if (this.ctx) return;
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
      
      this.mainGain = this.ctx.createGain();
      this.mainGain.gain.value = 0;
      
      this.filter = this.ctx.createBiquadFilter();
      this.filter.type = 'lowpass';
      this.filter.frequency.setValueAtTime(800, this.ctx.currentTime);
      
      this.mainGain.connect(this.filter);
      this.filter.connect(this.ctx.destination);
    }

    createPad(freq, detune = 2) {
      const oscs = [];
      const padGain = this.ctx.createGain();
      padGain.gain.value = 0.03;
      padGain.connect(this.mainGain);

      [0, detune, -detune].forEach(d => {
        const osc = this.ctx.createOscillator();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
        osc.detune.setValueAtTime(d, this.ctx.currentTime);
        osc.connect(padGain);
        osc.start();
        oscs.push(osc);
      });

      return { padGain, oscs };
    }

    playPianoNote(freq, time) {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, time);
      
      gain.gain.setValueAtTime(0, time);
      gain.gain.linearRampToValueAtTime(0.08, time + 0.05);
      gain.gain.exponentialRampToValueAtTime(0.001, time + 3);
      
      osc.connect(gain);
      gain.connect(this.mainGain);
      
      osc.start(time);
      osc.stop(time + 3.1);
    }

    start() {
      if (this.isStarted) return;
      this.init();
      if (this.ctx.state === 'suspended') this.ctx.resume();

      const now = this.ctx.currentTime;

      const rootPad = this.createPad(130.81);
      const fifthPad = this.createPad(196.00);
      
      const chords = [
        [261.63, 329.63, 392.00],
        [220.00, 261.63, 329.63],
        [349.23, 440.00, 523.25],
        [392.00, 493.88, 587.33]
      ];
      
      let chordIdx = 0;
      const chordLoop = setInterval(() => {
        const time = this.ctx.currentTime;
        const notes = chords[chordIdx];
        notes.forEach(f => this.playPianoNote(f, time));
        chordIdx = (chordIdx + 1) % chords.length;
      }, 4000);
      
      this.intervals.push(chordLoop);

      const sparkLoop = setInterval(() => {
        const time = this.ctx.currentTime;
        const sparks = [523.25, 659.25, 783.99, 1046.50];
        const freq = sparks[Math.floor(Math.random() * sparks.length)];
        this.playPianoNote(freq, time + Math.random());
      }, 2500);

      this.intervals.push(sparkLoop);

      this.mainGain.gain.linearRampToValueAtTime(0.15, now + 2);
      this.isStarted = true;
    }

    stop(fadeDuration = 0.1) {
      if (!this.ctx) return;
      this.isStarted = false;
      this.intervals.forEach(clearInterval);
      
      const now = this.ctx.currentTime;
      this.mainGain.gain.cancelScheduledValues(now);
      this.mainGain.gain.linearRampToValueAtTime(0, now + fadeDuration);
      
      setTimeout(() => {
        if (this.ctx) this.ctx.close();
        this.ctx = null;
      }, fadeDuration * 1000 + 50);
    }
  }

  const audioSystem = new ALISAudioSystem();

  const goNext = () => {
    audioSystem.stop(); // Stop immediately
    try { window.localStorage.setItem(INTRO_SEEN_KEY, "1"); } catch { }
    window.location.assign(NEXT_URL);
  };

  skipBtn.addEventListener("click", goNext);
  initBtn.addEventListener("click", goNext);

  const tl = gsap.timeline({
    onUpdate: () => {
      progressFill.style.width = `${tl.progress() * 100}%`;
    },
    onComplete: () => {
      audioSystem.stop(); // Stop immediately
      window.location.assign(NEXT_URL);
    }
  });

  const setCaption = (text) => {
    return gsap.timeline()
      .to(caption, { opacity: 0, y: 10, duration: 0.4 })
      .add(() => { caption.textContent = text; })
      .to(caption, { opacity: 1, y: 0, duration: 0.6 });
  };

  // INITIAL STATE
  gsap.set([s1, s2, s3, s4, s5, s6, s8, s9], { opacity: 0 });
  gsap.set([strengthCard, weaknessCard], { opacity: 0, scale: 0.9, y: 20 });

  // SEQUENCE START
  tl.add(() => audioSystem.start())
    .to(s1, { opacity: 1, duration: 1.5 })
    .add(setCaption("Every learner faces challenges."))
    .to("#confusion", { opacity: 1, y: -10, duration: 0.8, ease: "back.out" }, "-=0.5");

  tl.to(s2, { opacity: 1, duration: 1.5 }, "+=0.5")
    .add(setCaption("Not every learner learns the same way."))
    .to(s1, { x: -100, opacity: 0.3, duration: 1 }, "-=1");

  tl.to([s1, s2], { opacity: 0, duration: 0.8 }, "+=0.5")
    .add(setCaption("ALIS understands how you learn."))
    .to(s3, { opacity: 1, duration: 1.2 })
    .to(holoRing, { rotation: 360, transformOrigin: "50% 50%", duration: 4, repeat: 1, ease: "none" }, "-=1")
    .fromTo(scanPulse, { y: -200, opacity: 0 }, { y: 200, opacity: 0.8, duration: 2, repeat: 1, yoyo: true }, "-=2");

  tl.to(s3, { opacity: 0.1, scale: 0.8, duration: 1 })
    .add(setCaption("Discover strengths. Detect weaknesses."))
    .to(s4, { opacity: 1, duration: 1 })
    .to([strengthCard, weaknessCard], { opacity: 1, scale: 1, y: 0, duration: 1, stagger: 0.3, ease: "power3.out" }, "-=0.5");

  tl.to(s4, { opacity: 0, scale: 0.95, duration: 0.6 }, "+=2")
    .add(setCaption("A unique path for every learner."))
    .to(s5, { opacity: 1, duration: 1 })
    .to(activeRoadmap, { strokeDasharray: "1000 1000", duration: 3, ease: "power2.inOut" });

  tl.to(s5, { opacity: 0, duration: 0.6 }, "+=1")
    .add(setCaption("Smarter teaching. Better outcomes."))
    .to(s1, { opacity: 1, x: -250, y: 550, scale: 0.9, duration: 1.5, ease: "power2.inOut" })
    .to(s6, { opacity: 1, x: 0, duration: 1.5, ease: "power2.inOut" }, "-=1.5");

  tl.add(setCaption("Personalized learning creates growth."))
    .to(s6, { opacity: 0, duration: 1 }, "+=1.5")
    .to(s1, { x: 0, y: 550, scale: 1.1, opacity: 1, duration: 1.5, ease: "power2.inOut" }, "-=1")
    .add(setCaption("From confusion to mastery."))
    .to(s8, { opacity: 1, duration: 1 })
    .to(checkSuccess, { opacity: 1, strokeDasharray: "150 150", duration: 1, ease: "power2.out" }, "-=0.5");

  tl.to([s1, s8], { opacity: 0, filter: "blur(20px)", duration: 1.5 }, "+=1.5")
    .add(setCaption(""))
    .to(s9, { opacity: 1, scale: 1.05, duration: 2, ease: "power4.out" })
    .to(cta, { opacity: 1, pointerEvents: "auto", y: -40, duration: 1 }, "-=0.5");

})();
