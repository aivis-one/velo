// Backdrop — the rune-mandala layer used on auth, onboarding, and most app screens.
// Behind everything; opacity tuned so it never overpowers content.
const Backdrop = ({ variant = 'app', style = {} }) => {
  // variant:
  //   app       — soft, dashboard/detail screens; mandala-runes low opacity centered
  //   welcome   — strong, splash/onboarding; bigger, radial pink-peach glow under it
  //   auth      — medium, auth/oauth; centered high, glow behind
  //   onboarding— same as welcome but without inner mandala (scene dictates its own)
  const base = {
    position: 'absolute', inset: 0,
    pointerEvents: 'none',
    overflow: 'hidden',
    zIndex: 0,
  };
  return (
    <div style={{ ...base, ...style }}>
      {/* pink-peach radial glow */}
      <div style={{
        position: 'absolute',
        left: '50%', top: variant === 'welcome' ? '34%' : '38%',
        transform: 'translate(-50%, -50%)',
        width: variant === 'app' ? 520 : 640,
        height: variant === 'app' ? 520 : 640,
        background: 'radial-gradient(circle, rgba(247,149,162,0.38) 0%, rgba(254,236,219,0.28) 35%, rgba(226,240,253,0) 65%)',
        filter: 'blur(20px)',
      }} />
      {/* rune mandala */}
      <img src="../../assets/brand/mandala-runes.svg" alt=""
        style={{
          position: 'absolute',
          left: '50%', top: '50%',
          transform: 'translate(-50%, -50%)',
          width: variant === 'welcome' ? 780 : 720,
          height: variant === 'welcome' ? 780 : 720,
          opacity: variant === 'app' ? 0.28 : 0.5,
        }} />
    </div>
  );
};

window.Backdrop = Backdrop;
