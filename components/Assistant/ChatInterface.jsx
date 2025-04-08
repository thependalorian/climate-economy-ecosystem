"use client"

import { useState, useRef, useEffect } from 'react'
import { FiSend, FiPaperclip, FiUser, FiInfo } from 'react-icons/fi'
import { Button } from '../ui/Button'
import { Input } from '../ui/Form/Input'
import { Progress } from '../ui/progress'

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      content: "Hello! I'm your Climate Economy Assistant. I can help you find clean energy job opportunities, training programs, and resources to build your career in the clean energy sector. How can I help you today?",
      sender: 'assistant',
      timestamp: new Date().toISOString()
    }
  ])
  
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(true)
  const messagesEndRef = useRef(null)
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [messages])
  
  const suggestions = [
    "What clean energy jobs are available for someone with my skills?",
    "Tell me about training programs for solar installation",
    "What skills do I need for a career in wind energy?",
    "How can I transition from my current job to the clean energy sector?"
  ]
  
  const simulateTypingResponse = (userMessage) => {
    setIsLoading(true)
    
    // Simulate a delay to mimic AI processing
    setTimeout(() => {
      let response = ""
      
      if (userMessage.toLowerCase().includes('solar') || userMessage.toLowerCase().includes('installation')) {
        response = "There are many great opportunities in solar installation! The Massachusetts Clean Energy Center offers a Solar Training Network program, with courses ranging from basic installation to advanced system design. The average solar installer in Massachusetts earns $22-30 per hour. Would you like me to provide more specific training options or job opportunities in your area?"
      } else if (userMessage.toLowerCase().includes('wind') || userMessage.toLowerCase().includes('turbine')) {
        response = "Wind energy is growing rapidly in Massachusetts, especially with offshore wind projects. Entry-level technicians typically need mechanical skills, comfort working at heights, and safety training. The Bristol Community College offers a Wind Power Technology certificate program. The average wind technician salary is $54,000-$65,000 annually. Would you like more information about education requirements or job openings?"
      } else if (userMessage.toLowerCase().includes('transition') || userMessage.toLowerCase().includes('change career')) {
        response = "Transitioning to clean energy is a great choice! Many skills from traditional industries transfer well. For example, electricians can easily transition to solar installation, and HVAC technicians have valuable skills for energy efficiency work. The MassCEC Workforce Development program offers funding for training to help with career transitions. What's your current background, so I can suggest the best pathway for you?"
      } else {
        response = "Thank you for your question! The clean energy sector in Massachusetts offers many opportunities across solar, wind, energy efficiency, and more. To provide you with the most relevant information, could you tell me a bit more about your current skills, experience, and what areas of clean energy interest you most?"
      }
      
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        content: response,
        sender: 'assistant',
        timestamp: new Date().toISOString()
      }])
      
      setIsLoading(false)
    }, 2000)
  }
  
  const handleSendMessage = () => {
    if (!inputValue.trim()) return
    
    const newUserMessage = {
      id: messages.length + 1,
      content: inputValue,
      sender: 'user',
      timestamp: new Date().toISOString()
    }
    
    setMessages(prev => [...prev, newUserMessage])
    setInputValue('')
    setShowSuggestions(false)
    
    simulateTypingResponse(inputValue)
  }
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }
  
  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion)
    setShowSuggestions(false)
  }
  
  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg shadow overflow-hidden border border-gray-200">
      <div className="bg-primary text-white p-4">
        <div className="flex items-center">
          <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center mr-3">
            <FiInfo className="text-white text-xl" />
          </div>
          <div>
            <h3 className="font-bold">Climate Economy Assistant</h3>
            <p className="text-xs opacity-80">Helping you navigate clean energy opportunities</p>
          </div>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ scrollBehavior: 'smooth' }}>
        {messages.map(message => (
          <div 
            key={message.id} 
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div 
              className={`max-w-[80%] rounded-lg p-3 ${
                message.sender === 'user' 
                  ? 'bg-primary text-white rounded-br-none' 
                  : 'bg-gray-100 text-gray-800 rounded-bl-none'
              }`}
            >
              {message.content}
              <div className={`text-xs mt-1 ${message.sender === 'user' ? 'text-primary-content/70' : 'text-gray-500'}`}>
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-lg p-3 bg-gray-100 text-gray-800">
              <div className="flex space-x-2">
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0s' }}></div>
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {showSuggestions && messages.length === 1 && (
        <div className="px-4 py-2 bg-gray-50 border-t border-gray-200">
          <p className="text-xs text-gray-500 mb-2">Suggested questions:</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="text-xs bg-white border border-gray-300 rounded-full px-3 py-1 hover:bg-gray-100 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
      
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-2">
          <Button
            className="btn btn-circle btn-sm"
            onClick={() => {}}
          >
            <FiPaperclip />
          </Button>
          
          <div className="relative flex-1">
            <Input
              placeholder="Type a message..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full pr-10"
            />
          </div>
          
          <Button
            className="btn btn-primary btn-circle"
            disabled={!inputValue.trim() || isLoading}
            onClick={handleSendMessage}
          >
            <FiSend />
          </Button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface 