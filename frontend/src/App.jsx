import { Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import StudentChat from './pages/StudentChat';
import AboutPage from './pages/AboutPage';
import FAQPage from './pages/FAQPage';
import ProfessorLogin from './pages/ProfessorLogin';
import ProfessorRegister from './pages/ProfessorRegister';
import ProfessorDashboard from './pages/ProfessorDashboard';

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('professorToken');

  if (!token) {
    return <Navigate to="/professor" replace />;
  }

  return children;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/chat" element={<StudentChat />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/faq" element={<FAQPage />} />
      <Route path="/professor" element={<ProfessorLogin />} />
      <Route path="/professor/register" element={<ProfessorRegister />} />
      <Route
        path="/professor/dashboard"
        element={
          <ProtectedRoute>
            <ProfessorDashboard />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;
