// Main app — routes all screens. Flow:
// welcome → (login | register | onboarding) → oauth-loading → dashboard
// dashboard tabs jump to: calendar, practices list (home), my reservations (journal), check-in (+), profile
// any practice card → practice detail → booking detail → booking success → live
const App = () => {
  const [screen, setScreen] = React.useState('welcome');
  const [theme,  setTheme]  = React.useState('light');
  const [tab,    setTab]    = React.useState('home');
  const [oauthProvider, setOauthProvider] = React.useState('Google');

  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const goDashboard = () => { setTab('home'); setScreen('dashboard'); };
  const goLoadingThenDashboard = () => {
    setScreen('loading');
    setTimeout(goDashboard, 1200);
  };
  const goOAuth = (provider) => {
    setOauthProvider(provider);
    setScreen('oauth');
    setTimeout(goDashboard, 1400);
  };

  const onTab = (id) => {
    setTab(id);
    if (id === 'home')       setScreen('dashboard');
    else if (id === 'search')  setScreen('calendar');
    else if (id === 'plus')    setScreen('checkin');
    else if (id === 'journal') setScreen('reservations');
    else if (id === 'user')    setScreen('master');
  };

  return (
    <>
      {screen === 'welcome'     && <WelcomeScreen      onLogin={() => setScreen('auth')}
                                                       onRegister={() => setScreen('register')} />}
      {screen === 'onboarding'  && <OnboardingScreen   onDone={() => setScreen('welcome')} />}

      {screen === 'auth'        && <AuthScreen         onLogin={goLoadingThenDashboard}
                                                       onGoRegister={() => setScreen('register')}
                                                       onOAuth={goOAuth}
                                                       onBack={() => setScreen('welcome')} />}
      {screen === 'register'    && <RegisterScreen     onCreate={goLoadingThenDashboard}
                                                       onGoLogin={() => setScreen('auth')}
                                                       onOAuth={goOAuth}
                                                       onBack={() => setScreen('welcome')} />}
      {screen === 'oauth'       && <OAuthLoadingScreen provider={oauthProvider} />}

      {screen === 'dashboard'   && <DashboardScreen    theme={theme} setTheme={setTheme}
                                                       activeTab={tab} onTab={onTab}
                                                       onGoState={setScreen}
                                                       onOpenPractice={() => setScreen('practice')}
                                                       onOpenCheckIn={() => setScreen('checkin')}
                                                       onOpenBooking={() => setScreen('booking')} />}

      {screen === 'calendar'    && <CalendarScreen     onBack={goDashboard}
                                                       onOpenPractice={() => setScreen('practice')} />}
      {screen === 'practice'    && <PracticeDetailScreen onBack={() => setScreen('dashboard')}
                                                         onBook={() => setScreen('booking')} />}
      {screen === 'booking'     && <BookingDetailScreen onBack={() => setScreen('practice')}
                                                        onConfirm={() => setScreen('booking-success')}
                                                        onCancel={() => setScreen('dashboard')} />}
      {screen === 'booking-success' && <BookingSuccessScreen onGoCalendar={() => setScreen('calendar')}
                                                             onGoHome={goDashboard} />}

      {screen === 'master'      && <MasterProfileScreen onBack={goDashboard}
                                                        onBookPractice={() => setScreen('booking')} />}
      {screen === 'reservations'&& <MyReservationsScreen onBack={goDashboard}
                                                         onOpenBooking={() => setScreen('booking')} />}

      {screen === 'checkin'     && <CheckInScreen      onBack={goDashboard}
                                                       onSubmit={() => setScreen('checkin-success')} />}
      {screen === 'checkin-success' && <CheckInSuccessScreen onDone={goDashboard} />}
      {screen === 'ai-summary'  && <AISummaryScreen    onBack={goDashboard} />}
      {screen === 'live'        && <PracticeLiveScreen onBack={() => setScreen('practice')}
                                                       onLeave={goDashboard} />}

      {screen === 'loading'     && <LoadingScreen />}
      {screen === 'empty'       && <EmptyScreen        onRetry={goLoadingThenDashboard}
                                                       onBack={goDashboard} />}
      {screen === 'error'       && <ErrorScreen        onRetry={goLoadingThenDashboard}
                                                       onBack={goDashboard} />}
    </>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
