// MasterCard — Alex Mindful-style card with photo + name + tags + arrow pill
// Used on Practice Detail, Booking Detail, My Practice screens.
const MasterCard = ({ name, photo, tags = [], verified = true, onArrow }) => (
  <div style={{
    background: 'var(--surface-elevated)',
    borderRadius: 15,
    boxShadow: 'var(--shadow-md)',
    padding: 14,
    position: 'relative',
  }}>
    <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
      {/* Photo */}
      <div style={{
        width: 64, height: 64, borderRadius: 999,
        overflow: 'hidden', flex: '0 0 64px',
        background: 'var(--surface-muted)',
      }}>
        {photo
          ? <img src={photo} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }}/>
          : <Avatar size={64} initials={(name || '').split(' ').map(s=>s[0]).slice(0,2).join('')} color="teal" />}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
          <span style={{ fontSize: 17, color: 'var(--text-primary)' }}>{name}</span>
          {verified && (
            <span style={{
              width: 18, height: 18, borderRadius: 999,
              background: 'var(--accent-teal)', color: '#fff',
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
              flex: '0 0 18px',
            }}>
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                   strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </span>
          )}
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
          {tags.map((t, i) => (
            <Chip key={i} variant="tag" color={t.color || 'teal'}>{t.label}</Chip>
          ))}
        </div>
      </div>
    </div>
    {onArrow && (
      <div style={{
        display: 'flex', justifyContent: 'flex-end',
        marginTop: 10,
      }}>
        <ArrowPillButton onClick={onArrow} />
      </div>
    )}
  </div>
);

window.MasterCard = MasterCard;
