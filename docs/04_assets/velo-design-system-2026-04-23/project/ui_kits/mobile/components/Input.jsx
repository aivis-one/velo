// Input — 48px, md radius, focus uses teal 500 + soft ring.
const Input = ({ label, value, onChange, type = 'text', placeholder, error }) => {
  const [focused, setFocused] = React.useState(false);
  const borderColor = error
    ? 'var(--feedback-error)'
    : focused
    ? 'var(--accent-teal)'
    : 'var(--border-strong)';
  const shadow = focused && !error ? '0 0 0 3px rgba(47,158,168,0.15)' : 'none';
  return (
    <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {label && (
        <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{label}</span>
      )}
      <input
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange && onChange(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        style={{
          height: 48,
          borderRadius: 8,
          border: `1px solid ${borderColor}`,
          background: 'var(--surface-default)',
          color: 'var(--text-primary)',
          padding: '0 14px',
          fontFamily: 'var(--font-display)',
          fontSize: 15,
          outline: 'none',
          boxShadow: shadow,
          transition: 'border-color 150ms, box-shadow 150ms',
        }}
      />
      {error && (
        <span style={{ fontSize: 11, color: 'var(--feedback-error)' }}>{error}</span>
      )}
    </label>
  );
};

window.Input = Input;
