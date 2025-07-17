import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Navbar from './components/navbar';
import { navigationLinks } from './config/navigation';
import ScrollButton from './pages/scrollButton';

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        {navigationLinks.map(({ path, component: Component }) => (
          <Route key={path} path={path} element={<Component />} />
        ))}
        {/* Catch-all route to redirect to homepage */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
      <ScrollButton />
    </Router>
  );
}

export default App;