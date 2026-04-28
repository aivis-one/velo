// MandalaBackdrop — shared full-screen backdrop used across Welcome / Auth /
// Register / Onboarding / OAuth / Success screens. Single source of truth.
const MandalaBackdrop = ({ style = {} }) => (
  <div style={{
    position: 'absolute', inset: 0,
    background: '#E2F0FD',
    pointerEvents: 'none',
    ...style,
  }}>
    <img
      src="../../assets/brand/mandala-backdrop.png"
      alt=""
      style={{
        position: 'absolute', inset: 0,
        width: '100%', height: '100%',
        objectFit: 'cover',
      }}
    />
  </div>
);

window.MandalaBackdrop = MandalaBackdrop;
