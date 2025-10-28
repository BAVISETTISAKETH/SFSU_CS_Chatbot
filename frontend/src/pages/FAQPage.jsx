import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';

export default function FAQPage() {
  const navigate = useNavigate();
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      question: "What is the SFSU CS Chatbot?",
      answer: "The SFSU CS Chatbot is an AI-powered assistant designed to help students find information about the Computer Science department, courses, faculty, financial aid, international student services, and more. It uses advanced AI technology including Retrieval-Augmented Generation (RAG) and web search to provide accurate, helpful responses."
    },
    {
      question: "How does the chatbot work?",
      answer: "The chatbot uses a three-tier approach: 1) Verified Facts - Checks for professor-approved answers first, 2) RAG Search - Searches our knowledge base of SFSU documents, 3) Web Search - Fetches current information from the web when needed. This ensures you get the most accurate and up-to-date information."
    },
    {
      question: "What can I ask the chatbot?",
      answer: "You can ask about:\n• CS course requirements and descriptions\n• Faculty information and office hours\n• Financial aid and scholarships\n• International student services (CPT, OPT)\n• Housing and campus resources\n• Degree programs and graduation requirements\n• Academic policies and procedures\n• And much more!"
    },
    {
      question: "How accurate are the responses?",
      answer: "The chatbot is trained on official SFSU documents and web sources. Additionally, professors can review and correct responses to ensure accuracy. However, always verify critical information (like deadlines or requirements) with official SFSU sources or advisors."
    },
    {
      question: "What if the chatbot gives me an incorrect answer?",
      answer: "If you believe a response is incorrect, click the 'Flag as incorrect' button below the message. A professor will review the response and make corrections. This helps us continuously improve the chatbot's accuracy."
    },
    {
      question: "Is my conversation private?",
      answer: "Yes, your conversations are logged anonymously for quality improvement purposes, but no personally identifiable information is stored. We don't track who you are - only what questions are being asked to improve our answers."
    },
    {
      question: "Can the chatbot help with course registration?",
      answer: "The chatbot can provide information about course requirements, prerequisites, and offerings. However, for actual registration, you'll need to use SFSU's registration system. The chatbot can guide you to the right resources."
    },
    {
      question: "How do I export my chat history?",
      answer: "Click the 'Export' button in the top-right corner of the chat page. This will download a text file with your entire conversation that you can save for reference."
    },
    {
      question: "Does the chatbot support multiple languages?",
      answer: "Currently, the chatbot primarily supports English. However, it can understand and respond to basic questions in other languages to some extent."
    },
    {
      question: "What if I need help with something the chatbot can't answer?",
      answer: "If the chatbot can't help with your question, it will suggest contacting relevant departments or visiting specific SFSU resources. You can also reach out to academic advisors, the CS department office, or other appropriate SFSU offices directly."
    },
    {
      question: "Is this chatbot replacing human advisors?",
      answer: "No! This chatbot is designed to complement, not replace, human advisors and faculty. It's here to help with quick questions and general information, but complex academic planning, personal situations, and official decisions should still involve human advisors."
    },
    {
      question: "How often is the chatbot's knowledge updated?",
      answer: "The knowledge base is periodically updated with new documents and information. The web search feature ensures you get current information when needed. Professors can also add verified facts to keep information up-to-date."
    }
  ];

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
                FAQ
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="relative z-10 max-w-4xl mx-auto px-6 py-12">
        <div className="glass-strong rounded-3xl p-8 md:p-12 shadow-layers-purple">
          <h2 className="text-4xl font-bold gradient-text-animated mb-2">Frequently Asked Questions</h2>
          <p className="text-gray-300 mb-8">Find answers to common questions about the chatbot</p>

          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div
                key={index}
                className="glass-card rounded-2xl overflow-hidden hover-lift transition-all duration-300"
              >
                <button
                  onClick={() => setOpenIndex(openIndex === index ? null : index)}
                  className="w-full px-6 py-4 flex items-center justify-between text-left"
                >
                  <span className="font-semibold text-white pr-4">{faq.question}</span>
                  {openIndex === index ? (
                    <ChevronUp className="w-5 h-5 text-purple-400 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-purple-400 flex-shrink-0" />
                  )}
                </button>

                {openIndex === index && (
                  <div className="px-6 pb-4 text-gray-300 whitespace-pre-wrap animate-slideUp">
                    {faq.answer}
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="mt-8 p-6 glass-card rounded-2xl border-l-4 border-purple-500">
            <h3 className="text-lg font-bold gradient-text-purple mb-2">Still have questions?</h3>
            <p className="text-gray-300 text-sm mb-4">
              Try asking the chatbot directly! It's designed to answer your specific questions.
            </p>
            <button
              onClick={() => navigate('/chat')}
              className="px-6 py-3 rounded-xl text-white font-medium hover-lift-sfsu transition-all duration-300 shadow-layers-purple"
              style={{background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'}}
            >
              Ask the Chatbot
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
