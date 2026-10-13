import { useEffect, useRef } from 'react';
import './PoreField.css';

// Grid titik halus seperti pori kulit. Titik di sekitar kursor membesar dan
// berubah warna seperti lensa pemindai; klik atau tap memicu gelombang scan.
// Elemen-elemen yang cocok dengan quietSelector tetap bersih supaya teksnya terbaca.

const SPACING = 18;
const LENS_RADIUS = 130;
const RIPPLE_DURATION = 1100;
const RIPPLE_REACH = 480;
const BASE = { r: 0, g: 0, b: 0, a: 0.16 };
const HOT = { r: 194, g: 24, b: 91, a: 0.85 };

const mix = (from, to, t) => from + (to - from) * t;

const PoreField = ({ quietSelector }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const host = canvas.parentElement;
    const ctx = canvas.getContext('2d');
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    let width = 0;
    let height = 0;
    let pointer = null;
    let ripples = [];
    let frame = null;

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      width = host.clientWidth;
      height = host.clientHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      requestDraw();
    };

    const draw = (now) => {
      frame = null;
      ctx.clearRect(0, 0, width, height);
      const hostBox = host.getBoundingClientRect();
      const quiet = quietSelector
        ? [...host.querySelectorAll(quietSelector)].map((el) => el.getBoundingClientRect())
        : [];
      const pad = 20;
      const isQuiet = (x, y) =>
        quiet.some(
          (box) =>
            x > box.left - hostBox.left - pad &&
            x < box.right - hostBox.left + pad &&
            y > box.top - hostBox.top - pad &&
            y < box.bottom - hostBox.top + pad
        );
      ripples = ripples.filter((ripple) => now - ripple.start < RIPPLE_DURATION);

      for (let y = SPACING / 2; y < height; y += SPACING) {
        for (let x = SPACING / 2; x < width; x += SPACING) {
          if (isQuiet(x, y)) continue;
          let heat = 0;

          if (pointer) {
            const dist = Math.hypot(x - pointer.x, y - pointer.y);
            if (dist < LENS_RADIUS) heat = 1 - dist / LENS_RADIUS;
          }

          ripples.forEach((ripple) => {
            const progress = (now - ripple.start) / RIPPLE_DURATION;
            const ring = progress * RIPPLE_REACH;
            const band = Math.abs(Math.hypot(x - ripple.x, y - ripple.y) - ring);
            if (band < 28) heat = Math.max(heat, (1 - band / 28) * (1 - progress));
          });

          const eased = heat * heat;
          ctx.fillStyle = `rgba(${mix(BASE.r, HOT.r, eased)}, ${mix(BASE.g, HOT.g, eased)}, ${mix(BASE.b, HOT.b, eased)}, ${mix(BASE.a, HOT.a, eased)})`;
          ctx.beginPath();
          ctx.arc(x, y, 1 + eased * 2.2, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      if (ripples.length) requestDraw();
    };

    function requestDraw() {
      if (frame === null) frame = requestAnimationFrame(draw);
    }

    const toLocal = (e) => {
      const box = host.getBoundingClientRect();
      return { x: e.clientX - box.left, y: e.clientY - box.top };
    };

    const onMove = (e) => {
      if (e.pointerType !== 'mouse') return;
      pointer = toLocal(e);
      requestDraw();
    };

    const onLeave = () => {
      pointer = null;
      requestDraw();
    };

    const onDown = (e) => {
      if (reduceMotion) return;
      ripples.push({ ...toLocal(e), start: performance.now() });
      requestDraw();
    };

    const observer = new ResizeObserver(resize);
    observer.observe(host);
    // Form bisa berubah tinggi (field username, pesan error), jadi area bersih ikut diperbarui
    if (quietSelector) host.querySelectorAll(quietSelector).forEach((el) => observer.observe(el));
    host.addEventListener('pointermove', onMove);
    host.addEventListener('pointerleave', onLeave);
    host.addEventListener('pointerdown', onDown);

    return () => {
      observer.disconnect();
      host.removeEventListener('pointermove', onMove);
      host.removeEventListener('pointerleave', onLeave);
      host.removeEventListener('pointerdown', onDown);
      if (frame !== null) cancelAnimationFrame(frame);
    };
  }, [quietSelector]);

  return <canvas ref={canvasRef} className="pore-field" aria-hidden="true" />;
};

export default PoreField;
