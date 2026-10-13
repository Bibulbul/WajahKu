import { useEffect, useMemo, useRef } from 'react';
import './FaceDots.css';

// Wajah dari titik-titik, seperti pori kulit yang sedang dipindai.
// mood: 'idle' | 'watching' | 'shy' | 'busy' | 'sad'

const SIZE = 240;
const CENTER = SIZE / 2;
const EYES = [
  { x: 98, y: 108 },
  { x: 142, y: 108 },
];
const PUPIL_REACH = 6;

// Generator acak dengan seed tetap supaya susunan titik sama di setiap render
const seeded = (seed) => () => {
  seed = (seed * 16807) % 2147483647;
  return (seed - 1) / 2147483646;
};

const buildDots = () => {
  const rand = seeded(7);
  const dots = [];
  for (let i = 0; i < 220; i++) {
    const angle = rand() * Math.PI * 2;
    // Lebih rapat di tepi, jarang di tengah
    const radius = 62 + Math.sqrt(rand()) * 50;
    const x = CENTER + Math.cos(angle) * radius;
    const y = CENTER + Math.sin(angle) * radius * 1.08;
    dots.push({
      x,
      y,
      r: 1.2 + rand() * 2,
      delay: (Math.hypot(x - CENTER, y - CENTER) / 110).toFixed(2),
    });
  }
  return dots;
};

const FaceDots = ({ mood = 'idle', shakeKey = 0, lookDirection = { x: 1, y: 0.35 } }) => {
  const dots = useMemo(() => buildDots(), []);
  const svgRef = useRef(null);
  const pupilRefs = useRef([]);
  const target = useRef({ x: 0, y: 0 });
  const moodRef = useRef(mood);
  const lookRef = useRef(lookDirection);

  useEffect(() => {
    moodRef.current = mood;
    lookRef.current = lookDirection;
  }, [mood, lookDirection]);

  // Pupil mengikuti kursor. Tanpa kursor (layar sentuh), mata melirik sendiri.
  useEffect(() => {
    let frame;
    let lastPointer = 0;
    const current = { x: 0, y: 0 };
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const onPointerMove = (e) => {
      if (e.pointerType !== 'mouse' || !svgRef.current) return;
      lastPointer = performance.now();
      const box = svgRef.current.getBoundingClientRect();
      const dx = e.clientX - (box.left + box.width / 2);
      const dy = e.clientY - (box.top + box.height / 2);
      const dist = Math.hypot(dx, dy) || 1;
      const strength = Math.min(dist / 300, 1);
      target.current = { x: (dx / dist) * strength, y: (dy / dist) * strength };
    };

    const wander = setInterval(() => {
      if (performance.now() - lastPointer < 3000 || moodRef.current !== 'idle') return;
      target.current = { x: Math.random() * 2 - 1, y: Math.random() * 1.2 - 0.6 };
    }, 2600);

    const tick = () => {
      const goal = moodRef.current === 'watching' ? lookRef.current : target.current;
      const ease = reduceMotion ? 1 : 0.18;
      current.x += (goal.x - current.x) * ease;
      current.y += (goal.y - current.y) * ease;
      pupilRefs.current.forEach((pupil) => {
        pupil?.setAttribute(
          'transform',
          `translate(${(current.x * PUPIL_REACH).toFixed(2)} ${(current.y * PUPIL_REACH).toFixed(2)})`
        );
      });
      frame = requestAnimationFrame(tick);
    };

    window.addEventListener('pointermove', onPointerMove);
    frame = requestAnimationFrame(tick);
    return () => {
      window.removeEventListener('pointermove', onPointerMove);
      clearInterval(wander);
      cancelAnimationFrame(frame);
    };
  }, []);

  // Geleng kepala setiap ada error baru
  useEffect(() => {
    const svg = svgRef.current;
    if (!shakeKey || !svg) return;
    svg.classList.remove('is-shaking');
    void svg.getBoundingClientRect();
    svg.classList.add('is-shaking');
  }, [shakeKey]);

  return (
    <svg
      ref={svgRef}
      className={`face-dots mood-${mood}`}
      viewBox={`0 0 ${SIZE} ${SIZE}`}
      role="img"
      aria-label="Ilustrasi wajah dari titik-titik"
    >
      <g className="face-dots-skin">
        {dots.map((dot, i) => (
          <circle
            key={i}
            cx={dot.x.toFixed(1)}
            cy={dot.y.toFixed(1)}
            r={dot.r.toFixed(1)}
            style={{ '--d': `${dot.delay}s` }}
          />
        ))}
      </g>

      {EYES.map((eye, i) => (
        <g key={i} className="face-dots-eye" style={{ transformOrigin: `${eye.x}px ${eye.y}px` }}>
          <circle className="face-dots-sclera" cx={eye.x} cy={eye.y} r="14" />
          <circle
            ref={(el) => (pupilRefs.current[i] = el)}
            className="face-dots-pupil"
            cx={eye.x}
            cy={eye.y}
            r="7"
          />
        </g>
      ))}

      <circle className="face-dots-nose" cx={CENTER} cy="128" r="8" />
      <path
        className="face-dots-mouth"
        d={mood === 'sad' ? 'M106 158 Q120 148 134 158' : 'M106 150 Q120 160 134 150'}
      />
    </svg>
  );
};

export default FaceDots;
