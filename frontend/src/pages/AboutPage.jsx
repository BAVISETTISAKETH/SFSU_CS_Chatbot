import { useNavigate } from 'react-router-dom';
import { Home, Sparkles, Bot, Database, Zap, Shield } from 'lucide-react';

export default function AboutPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen relative overflow-hidden bg-slate-950">
      {/* Animated Background - DARK MODE */}
      <div className="absolute inset-0 bg-gradient-to-br from-black via-gray-900 to-black animate-gradient"></div>

      {/* Mesh Background - DARK MODE */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 -left-4 w-72 h-72 rounded-full mix-blend-screen filter blur-3xl animate-float" style={{background: '#1a1a1a'}}></div>
        <div className="absolute top-0 -right-4 w-72 h-72 rounded-full mix-blend-screen filter blur-3xl animate-float" style={{background: '#2a2a2a', animationDelay: '2s'}}></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 rounded-full mix-blend-screen filter blur-3xl animate-float" style={{background: '#0a0a0a', animationDelay: '4s'}}></div>
      </div>

      {/* Header */}
      <header className="relative z-10 glass-dark border-b border-white/10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/')}
              className="glass px-4 py-2 rounded-xl text-white hover-lift transition-all duration-300 flex items-center gap-2"
            >
              <Home className="w-4 h-4" />
              Home
            </button>
            <div>
              <h1 className="text-2xl font-bold gradient-text-animated flex items-center gap-2">
                <Sparkles className="w-6 h-6" style={{color: '#B4975A'}} />
                About
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="relative z-10 max-w-4xl mx-auto px-6 py-12">
        <div className="glass-strong rounded-3xl p-8 md:p-12 shadow-layers-purple">
          <h2 className="text-4xl font-bold gradient-text-animated mb-6">About SFSU CS Chatbot</h2>

          <div className="space-y-6 text-gray-200 leading-relaxed">
            <p className="text-lg">
              Welcome to the San Francisco State University Computer Science Chatbot - your intelligent
              AI assistant powered by cutting-edge technology!
            </p>

            <div className="grid md:grid-cols-2 gap-6 mt-8">
              <div className="glass-card p-6 rounded-2xl hover-lift">
                <Bot className="w-12 h-12 mb-4" style={{color: '#B4975A'}} />
                <h3 className="text-xl font-bold gradient-text-gold mb-2">AI-Powered</h3>
                <p className="text-sm text-gray-300">
                  Powered by Groq's Llama 3.3 70B model for natural, conversational responses
                </p>
              </div>

              <div className="glass-card p-6 rounded-2xl hover-lift">
                <Database className="w-12 h-12 mb-4" style={{color: '#B4975A'}} />
                <h3 className="text-xl font-bold gradient-text-gold mb-2">RAG Technology</h3>
                <p className="text-sm text-gray-300">
                  Uses Retrieval-Augmented Generation with Supabase vector database
                </p>
              </div>

              <div className="glass-card p-6 rounded-2xl hover-lift">
                <Zap className="w-12 h-12 mb-4" style={{color: '#B4975A'}} />
                <h3 className="text-xl font-bold gradient-text-gold mb-2">Web Search</h3>
                <p className="text-sm text-gray-300">
                  Fetches real-time information when needed for up-to-date answers
                </p>
              </div>

              <div className="glass-card p-6 rounded-2xl hover-lift">
                <Shield className="w-12 h-12 mb-4" style={{color: '#B4975A'}} />
                <h3 className="text-xl font-bold gradient-text-gold mb-2">Professor Verified</h3>
                <p className="text-sm text-gray-300">
                  Professors can review and correct responses to ensure accuracy
                </p>
              </div>
            </div>

            <div className="mt-8 p-6 glass-card rounded-2xl border-l-4 border-purple-500">
              <h3 className="text-xl font-bold gradient-text-purple mb-3">What Can I Ask?</h3>
              <ul className="space-y-2 text-gray-300">
                <li>• Course requirements and descriptions</li>
                <li>• Faculty information and office hours</li>
                <li>• Financial aid and scholarships</li>
                <li>• International student services (CPT, OPT)</li>
                <li>• Housing and campus resources</li>
                <li>• Degree programs and graduation requirements</li>
              </ul>
            </div>

            <div className="mt-8 p-6 glass-card rounded-2xl bg-gradient-to-br from-purple-500/10 to-pink-500/10">
              <h3 className="text-xl font-bold gradient-text-animated mb-3">Technology Stack</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                <div className="bg-white/5 px-3 py-2 rounded-lg">Groq AI (Llama 3.3)</div>
                <div className="bg-white/5 px-3 py-2 rounded-lg">Supabase (pgvector)</div>
                <div className="bg-white/5 px-3 py-2 rounded-lg">FastAPI</div>
                <div className="bg-white/5 px-3 py-2 rounded-lg">React</div>
                <div className="bg-white/5 px-3 py-2 rounded-lg">SerpAPI</div>
                <div className="bg-white/5 px-3 py-2 rounded-lg">BeautifulSoup4</div>
              </div>
            </div>
          </div>

          <div className="mt-8 flex justify-center">
            <button
              onClick={() => navigate('/chat')}
              className="px-8 py-4 rounded-2xl text-white font-medium hover-lift-sfsu transition-all duration-300 shadow-layers-purple flex items-center gap-2"
              style={{background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'}}
            >
              <Sparkles className="w-5 h-5" />
              Start Chatting
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
