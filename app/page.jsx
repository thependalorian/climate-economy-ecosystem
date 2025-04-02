"use client";

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useSession } from 'next-auth/react';
import { FileText, Briefcase, GraduationCap, Users, MapPin, ArrowRight, BarChart2, Check, Star, Globe, Award } from 'lucide-react';

export default function Home() {
  const { data: session } = useSession();
  const [activePersona, setActivePersona] = useState('veteran');

  // Sample assistant responses for different personas
  const personaResponses = {
    veteran: "Based on your military experience as a Logistics Specialist, I recommend exploring renewable energy supply chain roles. Your leadership skills and logistics expertise translate well to solar deployment coordination.",
    international: "With your engineering degree from University of Lagos, you qualify for many positions in Massachusetts. I recommend the Professional Engineering exam prep course at Bunker Hill Community College as your next step.",
    student: "As a community college student in environmental science, I recommend the Clean Energy Certificate program and these 3 internship opportunities with ACT member companies in Boston.",
    ej: "Living in an Environmental Justice community in Lawrence gives you priority access to these 5 training programs with stipends and transportation assistance. The Merrimack Valley Clean Energy Training has a 94% job placement rate.",
    reentry: "Returning to the workforce after 5 years, your previous experience in manufacturing transfers well to solar panel production. These 3 companies in Worcester offer returnship programs."
  };

  return (
    <main className="bg-white">
      {/* Hero Section - No Navbar, Image-Focused */}
      <section className="relative overflow-hidden">
        {/* Background image */}
        <div className="absolute inset-0 z-0">
          <Image 
            src="/images/hero-solar-installation.jpg" 
            alt="Clean energy professionals installing solar panels"
            layout="fill"
            objectFit="cover"
            priority
          />
          <div className="absolute inset-0 bg-midnight-forest bg-opacity-60 mix-blend-multiply"></div>
        </div>
        
        <div className="container mx-auto relative z-10 py-20 md:py-32 px-4">
          <div className="flex flex-col lg:flex-row items-center gap-8">
            {/* Left content column */}
            <div className="lg:w-1/2 max-w-2xl text-white">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
                Accelerate Your <span className="text-spring-green">Clean Energy Career</span> in Massachusetts
              </h1>
              
              <p className="text-xl mb-8">
                Connect with personalized job matches, training programs, and resources tailored to your skills and experience.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                {session ? (
                  <Link href="/dashboard" className="btn btn-primary btn-lg">
                    Go to Dashboard
                  </Link>
                ) : (
                  <Link href="/auth/signup" className="btn btn-primary btn-lg group">
                    Start Your Journey <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" />
                  </Link>
                )}
                
                <Link href="#how-it-works" className="btn bg-white text-midnight-forest border-white btn-lg hover:bg-gray-100">
                  How It Works
                </Link>
              </div>
              
              <div className="flex items-center gap-6 flex-wrap">
                <div className="flex items-center gap-2">
                  <div className="bg-spring-green rounded-full p-1">
                    <Check size={16} className="text-midnight-forest" />
                  </div>
                  <span className="text-white">Free access</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="bg-spring-green rounded-full p-1">
                    <Check size={16} className="text-midnight-forest" />
                  </div>
                  <span className="text-white">Personalized guidance</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="bg-spring-green rounded-full p-1">
                    <Check size={16} className="text-midnight-forest" />
                  </div>
                  <span className="text-white">AI-powered matching</span>
                </div>
              </div>
            </div>
            
            {/* Right image/visual column - Assistant Showcase */}
            <div className="lg:w-1/2 relative">
              <div className="bg-white rounded-lg overflow-hidden shadow-xl border border-gray-200">
                <div className="p-6 bg-seafoam-blue bg-opacity-20 border-b border-gray-200">
                  <h2 className="text-2xl font-bold text-midnight-forest flex items-center">
                    <FileText size={24} className="text-spring-green mr-2" />
                    Climate Economy Assistant
                  </h2>
                </div>
                
                <div className="p-6">
                  {/* Persona selector */}
                  <div className="flex flex-wrap gap-2 mb-6">
                    <button 
                      onClick={() => setActivePersona('veteran')}
                      className={`px-3 py-1 text-sm rounded-full ${activePersona === 'veteran' ? 'bg-spring-green text-midnight-forest' : 'bg-gray-100'}`}
                    >
                      Military Veteran
                    </button>
                    <button 
                      onClick={() => setActivePersona('international')}
                      className={`px-3 py-1 text-sm rounded-full ${activePersona === 'international' ? 'bg-spring-green text-midnight-forest' : 'bg-gray-100'}`}
                    >
                      International Professional
                    </button>
                    <button 
                      onClick={() => setActivePersona('student')}
                      className={`px-3 py-1 text-sm rounded-full ${activePersona === 'student' ? 'bg-spring-green text-midnight-forest' : 'bg-gray-100'}`}
                    >
                      Student
                    </button>
                    <button 
                      onClick={() => setActivePersona('ej')}
                      className={`px-3 py-1 text-sm rounded-full ${activePersona === 'ej' ? 'bg-spring-green text-midnight-forest' : 'bg-gray-100'}`}
                    >
                      EJ Community
                    </button>
                    <button 
                      onClick={() => setActivePersona('reentry')}
                      className={`px-3 py-1 text-sm rounded-full ${activePersona === 'reentry' ? 'bg-spring-green text-midnight-forest' : 'bg-gray-100'}`}
                    >
                      Workforce Reentry
                    </button>
                  </div>
                  
                  {/* Assistant conversation mockup */}
                  <div className="bg-gray-50 rounded-lg p-4 mb-4">
                    <div className="flex gap-3 mb-3">
                      <div className="w-8 h-8 rounded-full bg-gray-200 flex-shrink-0 flex items-center justify-center">
                        <Users size={16} className="text-gray-500" />
                      </div>
                      <div>
                        <p className="text-gray-800">How can my background help me find a job in clean energy?</p>
                      </div>
                    </div>
                    
                    <div className="flex gap-3">
                      <div className="w-8 h-8 rounded-full bg-spring-green flex-shrink-0 flex items-center justify-center">
                        <FileText size={16} className="text-midnight-forest" />
                      </div>
                      <div>
                        <p className="text-gray-800">{personaResponses[activePersona]}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Ask the Climate Economy Assistant..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg pr-12"
                      disabled
                    />
                    <button className="absolute right-3 top-1/2 transform -translate-y-1/2 bg-spring-green p-2 rounded-full">
                      <ArrowRight size={16} className="text-midnight-forest" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Strip */}
      <section className="py-8 bg-white border-y border-gray-100">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <div className="flex flex-col items-center text-center">
              <span className="text-3xl font-bold text-spring-green mb-2">340+</span>
              <span className="text-gray-700">Clean energy companies</span>
            </div>
            <div className="flex flex-col items-center text-center">
              <span className="text-3xl font-bold text-spring-green mb-2">1000s</span>
              <span className="text-gray-700">Of job opportunities</span>
            </div>
            <div className="flex flex-col items-center text-center">
              <span className="text-3xl font-bold text-spring-green mb-2">94%</span>
              <span className="text-gray-700">User satisfaction rate</span>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section - Image-Rich */}
      <section id="how-it-works" className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-midnight-forest">
            How It Works
          </h2>
          <p className="text-center text-gray-600 max-w-2xl mx-auto mb-12">
            A simple 4-step process to match you with the perfect clean energy opportunities
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 max-w-5xl mx-auto">
            <div className="flex flex-col items-center text-center">
              <div className="mb-6 rounded-lg overflow-hidden w-48 h-48 relative">
                <Image 
                  src="/images/signup-process.jpg" 
                  alt="Person signing up on laptop"
                  layout="fill"
                  objectFit="cover"
                />
                <div className="absolute bottom-0 left-0 bg-spring-green text-midnight-forest font-bold text-xl w-10 h-10 flex items-center justify-center rounded-tr-lg">
                  1
                </div>
              </div>
              <h3 className="text-xl font-bold mb-3 text-midnight-forest">Sign Up</h3>
              <p className="text-gray-600">Create your free account in less than 2 minutes</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
              <div className="mb-6 rounded-lg overflow-hidden w-48 h-48 relative">
                <Image 
                  src="/images/profile-creation.jpg" 
                  alt="Person filling out profile information"
                  layout="fill"
                  objectFit="cover"
                />
                <div className="absolute bottom-0 left-0 bg-spring-green text-midnight-forest font-bold text-xl w-10 h-10 flex items-center justify-center rounded-tr-lg">
                  2
                </div>
              </div>
              <h3 className="text-xl font-bold mb-3 text-midnight-forest">Share Your Background</h3>
              <p className="text-gray-600">Tell us about your skills, experience, and career goals</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
              <div className="mb-6 rounded-lg overflow-hidden w-48 h-48 relative">
                <Image 
                  src="/images/ai-matching.jpg" 
                  alt="AI matching visualization"
                  layout="fill"
                  objectFit="cover"
                />
                <div className="absolute bottom-0 left-0 bg-spring-green text-midnight-forest font-bold text-xl w-10 h-10 flex items-center justify-center rounded-tr-lg">
                  3
                </div>
              </div>
              <h3 className="text-xl font-bold mb-3 text-midnight-forest">Get Matched</h3>
              <p className="text-gray-600">Receive personalized job and training recommendations</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
              <div className="mb-6 rounded-lg overflow-hidden w-48 h-48 relative">
                <Image 
                  src="/images/career-start.jpg" 
                  alt="Person starting new job in clean energy"
                  layout="fill"
                  objectFit="cover"
                />
                <div className="absolute bottom-0 left-0 bg-spring-green text-midnight-forest font-bold text-xl w-10 h-10 flex items-center justify-center rounded-tr-lg">
                  4
                </div>
              </div>
              <h3 className="text-xl font-bold mb-3 text-midnight-forest">Take Action</h3>
              <p className="text-gray-600">Apply to jobs and access training resources</p>
            </div>
          </div>
          
          <div className="flex justify-center mt-12">
            <Link href="/auth/signup" className="btn btn-primary btn-lg group">
              Get Started Now <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>
      </section>

      {/* Key Features Section - Image-Based */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-midnight-forest">
            Key Features
          </h2>
          <p className="text-center text-gray-600 max-w-2xl mx-auto mb-12">
            Tools and resources to accelerate your clean energy career
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="bg-white rounded-lg overflow-hidden shadow border border-gray-200">
              <div className="h-48 relative">
                <Image 
                  src="/images/job-matching.jpg" 
                  alt="AI job matching visualization"
                  layout="fill"
                  objectFit="cover"
                />
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold mb-4 text-midnight-forest">AI-Powered Job Matching</h3>
                <p className="text-gray-600">
                  Our intelligent assistant analyzes your background and recommends the perfect opportunities in the clean energy sector.
                </p>
              </div>
            </div>
            
            <div className="bg-white rounded-lg overflow-hidden shadow border border-gray-200">
              <div className="h-48 relative">
                <Image 
                  src="/images/skills-analysis.jpg" 
                  alt="Skills gap analysis visualization"
                  layout="fill"
                  objectFit="cover"
                />
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold mb-4 text-midnight-forest">Skills Gap Analysis</h3>
                <p className="text-gray-600">
                  Identify what skills you need to develop for your desired clean energy role and get personalized training recommendations.
                </p>
              </div>
            </div>
            
            <div className="bg-white rounded-lg overflow-hidden shadow border border-gray-200">
              <div className="h-48 relative">
                <Image 
                  src="/images/career-planning.jpg" 
                  alt="Career pathway planning session"
                  layout="fill"
                  objectFit="cover"
                />
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold mb-4 text-midnight-forest">Career Pathway Planning</h3>
                <p className="text-gray-600">
                  Map out your journey in the clean energy sector with personalized career roadmaps and growth opportunities.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section - Changed to Invitation */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-midnight-forest">
            Be Part of Our Success Story
          </h2>
          <p className="text-center text-gray-600 max-w-2xl mx-auto mb-12">
            Join our growing community and help shape the future of clean energy careers in Massachusetts
          </p>
          
          <div className="max-w-3xl mx-auto bg-white rounded-lg shadow-lg p-8 text-center">
            <h3 className="text-xl font-bold text-midnight-forest mb-4">
              Early Access Program
            </h3>
            <p className="text-gray-600 mb-6">
              Be among the first to use our platform and share your journey in the clean energy economy. Your experience will help us improve and expand opportunities for others.
            </p>
            <Link href="/auth/signup" className="btn btn-primary btn-lg group">
              Join Now - It's Free <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>
      </section>

      {/* Communities Section */}
      <section className="py-20 bg-white relative">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-midnight-forest">
            For Our Communities
          </h2>
          <p className="text-center text-gray-600 max-w-2xl mx-auto mb-12">
            Specialized resources for diverse communities across Massachusetts
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <CommunityCard 
              title="Veterans"
              badge="Veterans"
              description="Military experience translates to valuable skills in clean energy. We help you demonstrate that value to employers."
              link="/resources/veterans"
              icon={<Users className="text-spring-green" size={24} />}
              image="/images/veterans-clean-energy.jpg"
            />
            
            <CommunityCard 
              title="Environmental Justice Communities"
              badge="EJ Communities"
              description="Resources for residents of EJ communities to access clean energy careers and local opportunities."
              link="/resources/ej-communities"
              icon={<MapPin className="text-spring-green" size={24} />}
              image="/images/ej-community.jpg"
            />
            
            <CommunityCard 
              title="International Professionals"
              badge="International"
              description="Guidance on credential translation and career pathways for skilled immigrants in clean tech."
              link="/resources/international"
              icon={<Globe className="text-spring-green" size={24} />}
              image="/images/international-professionals.jpg"
            />
          </div>
        </div>
      </section>
      
      {/* Partner Organizations Section - Enhanced */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-midnight-forest">
            Our Partner Network
          </h2>
          <p className="text-center text-gray-600 max-w-2xl mx-auto mb-12">
            Working with leading organizations to create pathways into the clean energy economy
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* MyHeadlamp */}
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <div className="h-16 relative mb-4">
                <Image 
                  src="/images/partners/myheadlamp.png"
                  alt="MyHeadlamp Logo"
                  layout="fill"
                  objectFit="contain"
                />
              </div>
              <h3 className="text-xl font-bold text-midnight-forest mb-2">MyHeadlamp</h3>
              <p className="text-gray-600 mb-4">
                Specializing in helping veterans translate their military experience into valuable clean energy careers through personalized career navigation.
              </p>
              <Link href="https://myheadlamp.com/" className="text-spring-green hover:underline flex items-center" target="_blank">
                Learn More <ArrowRight size={16} className="ml-1" />
              </Link>
            </div>

            {/* AfricanBN */}
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <div className="h-16 relative mb-4">
                <Image 
                  src="/images/partners/africanbn.png"
                  alt="African Bridge Network Logo"
                  layout="fill"
                  objectFit="contain"
                />
              </div>
              <h3 className="text-xl font-bold text-midnight-forest mb-2">African Bridge Network</h3>
              <p className="text-gray-600 mb-4">
                Supporting African immigrants in translating their professional experience and education for the Massachusetts clean energy workforce.
              </p>
              <Link href="https://africanbn.org/" className="text-spring-green hover:underline flex items-center" target="_blank">
                Learn More <ArrowRight size={16} className="ml-1" />
              </Link>
            </div>

            {/* ULEM */}
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <div className="h-16 relative mb-4">
                <Image 
                  src="/images/partners/ulem.png"
                  alt="ULEM Logo"
                  layout="fill"
                  objectFit="contain"
                />
              </div>
              <h3 className="text-xl font-bold text-midnight-forest mb-2">Urban League of Eastern MA</h3>
              <p className="text-gray-600 mb-4">
                Providing workforce development and training programs focused on environmental justice communities and creating equitable pathways to clean energy careers.
              </p>
              <Link href="https://www.ulem.org/" className="text-spring-green hover:underline flex items-center" target="_blank">
                Learn More <ArrowRight size={16} className="ml-1" />
              </Link>
            </div>

            {/* Franklin Cummings */}
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <div className="h-16 relative mb-4">
                <Image 
                  src="/images/partners/franklin-cummings.png"
                  alt="Franklin Cummings Tech Logo"
                  layout="fill"
                  objectFit="contain"
                />
              </div>
              <h3 className="text-xl font-bold text-midnight-forest mb-2">Franklin Cummings Tech</h3>
              <p className="text-gray-600 mb-4">
                Leading technical education provider offering specialized programs in HVAC/R, renewable energy, and building energy management for upskilling.
              </p>
              <Link href="https://franklincummings.edu/" className="text-spring-green hover:underline flex items-center" target="_blank">
                Learn More <ArrowRight size={16} className="ml-1" />
              </Link>
            </div>

            {/* MassHire */}
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <div className="h-16 relative mb-4">
                <Image 
                  src="/images/partners/masshire.png"
                  alt="MassHire Logo"
                  layout="fill"
                  objectFit="contain"
                />
              </div>
              <h3 className="text-xl font-bold text-midnight-forest mb-2">MassHire</h3>
              <p className="text-gray-600 mb-4">
                Comprehensive workforce development services including training programs, job placement, and specialized resources for clean energy careers.
              </p>
              <Link href="https://www.mass.gov/masshire-career-centers" className="text-spring-green hover:underline flex items-center" target="_blank">
                Learn More <ArrowRight size={16} className="ml-1" />
              </Link>
            </div>

            {/* MassCEC */}
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <div className="h-16 relative mb-4">
                <Image 
                  src="/images/partners/masscec.png"
                  alt="MassCEC Logo"
                  layout="fill"
                  objectFit="contain"
                />
              </div>
              <h3 className="text-xl font-bold text-midnight-forest mb-2">MassCEC</h3>
              <p className="text-gray-600 mb-4">
                State economic development agency dedicated to accelerating clean energy sector growth through workforce development and innovation programs.
              </p>
              <Link href="https://www.masscec.com/" className="text-spring-green hover:underline flex items-center" target="_blank">
                Learn More <ArrowRight size={16} className="ml-1" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section with Image Background */}
      <section className="py-20 relative">
        <div className="absolute inset-0 z-0">
          <Image 
            src="/images/clean-energy-team.jpg" 
            alt="Clean energy professionals working together"
            layout="fill"
            objectFit="cover"
          />
          <div className="absolute inset-0 bg-midnight-forest bg-opacity-70"></div>
        </div>
        
        <div className="container mx-auto px-4 relative z-10">
          <div className="bg-white/90 backdrop-blur p-12 mx-auto max-w-4xl rounded-lg relative overflow-hidden shadow-xl border border-gray-200">
            <h2 className="text-3xl md:text-4xl font-bold text-center mb-6 text-midnight-forest">
              Ready to Launch Your Clean Energy Career?
            </h2>
            <p className="text-xl mb-8 max-w-2xl mx-auto text-center text-gray-700">
              Join thousands of professionals who've found their place in the Massachusetts clean tech economy.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link href="/auth/signup" className="btn btn-primary btn-lg group">
                Create Your Free Account
                <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link href="/about" className="btn btn-outline btn-lg border-spring-green text-midnight-forest">
                Learn More
              </Link>
            </div>
            <div className="mt-8 flex justify-center gap-6 flex-wrap">
              <div className="flex items-center gap-2">
                <div className="bg-spring-green rounded-full p-1">
                  <Check size={16} className="text-midnight-forest" />
                </div>
                <span className="text-gray-700">Personalized matching</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="bg-spring-green rounded-full p-1">
                  <Check size={16} className="text-midnight-forest" />
                </div>
                <span className="text-gray-700">Free access</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="bg-spring-green rounded-full p-1">
                  <Check size={16} className="text-midnight-forest" />
                </div>
                <span className="text-gray-700">Private & secure</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

function CommunityCard({ title, badge, description, link, icon, image }) {
  return (
    <div className="bg-white rounded-lg overflow-hidden shadow border border-gray-200">
      <div className="h-48 relative">
        <Image 
          src={image} 
          alt={title}
          layout="fill"
          objectFit="cover"
        />
        <div className="absolute top-4 right-4 bg-spring-green px-3 py-1 rounded-full">
          <span className="text-midnight-forest text-sm font-medium">{badge}</span>
        </div>
      </div>
      
      <div className="p-6">
        <div className="flex items-center mb-4">
          <div className="bg-midnight-forest rounded-full p-3 mr-3">
            {icon}
          </div>
          <h3 className="text-xl font-bold text-midnight-forest">{title}</h3>
        </div>
        <p className="mb-6 text-gray-600">{description}</p>
        <div className="card-actions justify-end">
          <Link href={link} className="btn btn-secondary btn-sm">
            View Resources
          </Link>
        </div>
      </div>
    </div>
  );
}