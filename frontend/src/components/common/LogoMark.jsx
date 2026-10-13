import './LogoMark.css';

// Logo WajahKu: versi mini wajah titik-titik. Berkedip saat disentuh kursor.
const RING = Array.from({ length: 14 }, (_, i) => {
  const angle = (i / 14) * Math.PI * 2;
  return { x: 16 + Math.cos(angle) * 13, y: 16 + Math.sin(angle) * 13.5, r: i % 3 === 0 ? 1.7 : 1.2 };
});

const LogoMark = ({ className = '' }) => (
  <span className={`logo-mark ${className}`}>
    <svg viewBox="0 0 32 32" aria-hidden="true">
      {RING.map((dot, i) => (
        <circle key={i} cx={dot.x.toFixed(2)} cy={dot.y.toFixed(2)} r={dot.r} />
      ))}
      <g className="logo-mark-eyes">
        <circle cx="12.5" cy="14" r="2.4" />
        <circle cx="19.5" cy="14" r="2.4" />
      </g>
      <circle className="logo-mark-nose" cx="16" cy="19" r="1.6" />
    </svg>
    wajahku
  </span>
);

export default LogoMark;
