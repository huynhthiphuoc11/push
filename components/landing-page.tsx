"use client"

import { useState } from "react"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { Badge } from "../components/ui/badge"
import {
  Brain,
  Target,
  Zap,
  Users,
  TrendingUp,
  CheckCircle,
  ArrowRight,
  Upload,
  Search,
  BarChart3,
  Star,
  Quote,
  ChevronLeft,
  ChevronRight,
} from "lucide-react"
import Link from "next/link"

const testimonials = [
  {
    name: "Sarah Chen",
    role: "Software Engineer",
    company: "Tech Startup",
    content: "Found my dream job in just 2 weeks! The AI matching was incredibly accurate.",
    rating: 5,
  },
  {
    name: "Michael Nguyen",
    role: "Data Scientist",
    company: "Fortune 500",
    content: "The skill analysis helped me identify gaps and land a senior position.",
    rating: 5,
  },
  {
    name: "Emily Rodriguez",
    role: "Product Manager",
    company: "Scale-up",
    content: "Best job matching platform I've used. The recommendations were spot-on.",
    rating: 5,
  },
]

export function LandingPage() {
  const [currentTestimonial, setCurrentTestimonial] = useState(0)

  const nextTestimonial = () => {
    setCurrentTestimonial((prev) => (prev + 1) % testimonials.length)
  }

  const prevTestimonial = () => {
    setCurrentTestimonial((prev) => (prev - 1 + testimonials.length) % testimonials.length)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-purple-600" />
              <span className="text-xl font-bold font-sans">CareerMatch AI</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/upload">
                <Button variant="outline" className="font-sans bg-transparent">
                  Upload CV
                </Button>
              </Link>
              <Link href="/jobs">
                <Button className="bg-purple-600 hover:bg-purple-700 font-sans">Browse Jobs</Button>
              </Link>
              <Link href="/industry-trends">
                <Button className="bg-blue-600 hover:bg-blue-700 text-white font-sans">Xu hướng ngành IT</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl text-center">
          <div className="mb-8">
            <Badge className="bg-purple-100 text-purple-800 hover:bg-purple-200 mb-4 font-sans">
              <Zap className="h-3 w-3 mr-1" />
              AI-Powered Matching
            </Badge>
            <h1 className="text-5xl md:text-6xl font-bold text-gray-800 mb-6 font-sans leading-tight">
              Unlock Your Career Potential with <span className="text-purple-600">AI-Driven Insights</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto font-sans leading-relaxed">
              Effortlessly match your CV to the best job opportunities tailored for you. Our advanced AI analyzes your
              skills, experience, and preferences to connect you with perfect career matches.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/upload">
                <Button size="lg" className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-4 text-lg font-sans">
                  Get Started Today
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link href="/jobs">
                <Button size="lg" variant="outline" className="px-8 py-4 text-lg font-sans bg-transparent">
                  Browse Jobs
                </Button>
              </Link>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-600 mb-2 font-sans">95%</div>
              <div className="text-gray-600 font-sans">Match Accuracy</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-600 mb-2 font-sans">10K+</div>
              <div className="text-gray-600 font-sans">Jobs Matched</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-600 mb-2 font-sans">2.5x</div>
              <div className="text-gray-600 font-sans">Faster Job Search</div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-800 mb-4 font-sans">How Our AI Works</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto font-sans">
              Our sophisticated AI pipeline analyzes your CV and matches you with opportunities using cutting-edge
              technology
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="text-center border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="mx-auto w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                  <Upload className="h-8 w-8 text-purple-600" />
                </div>
                <CardTitle className="font-sans">1. Upload & Parse</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base font-sans">
                  Upload your CV and our AI extracts key information: skills, experience, education, and contact details
                  with 99% accuracy.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="text-center border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="mx-auto w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                  <Brain className="h-8 w-8 text-purple-600" />
                </div>
                <CardTitle className="font-sans">2. AI Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base font-sans">
                  Advanced BART→SBERT→LTR pipeline analyzes semantic similarity between your profile and job
                  requirements.
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="text-center border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="mx-auto w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                  <Target className="h-8 w-8 text-purple-600" />
                </div>
                <CardTitle className="font-sans">3. Perfect Matches</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base font-sans">
                  Get ranked job recommendations with detailed matching analysis, skill gaps, and application insights.
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-800 mb-4 font-sans">Powerful Features</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto font-sans">
              Everything you need to accelerate your job search and land your dream role
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Search className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 font-sans">Smart Job Search</h3>
                <p className="text-gray-600 font-sans">
                  AI-powered search that understands context and finds relevant opportunities beyond keyword matching.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <BarChart3 className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 font-sans">Skill Gap Analysis</h3>
                <p className="text-gray-600 font-sans">
                  Identify missing skills and get personalized recommendations to improve your competitiveness.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 font-sans">Match Scoring</h3>
                <p className="text-gray-600 font-sans">
                  Get detailed match scores with explanations for why each job is recommended for you.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Users className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 font-sans">Company Insights</h3>
                <p className="text-gray-600 font-sans">
                  Learn about company culture, salary ranges, and growth opportunities before applying.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <CheckCircle className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 font-sans">Application Tracking</h3>
                <p className="text-gray-600 font-sans">
                  Keep track of your applications and get insights on your job search progress.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Zap className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2 font-sans">Real-time Updates</h3>
                <p className="text-gray-600 font-sans">
                  Get notified instantly when new jobs matching your profile become available.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-800 mb-4 font-sans">Success Stories</h2>
            <p className="text-xl text-gray-600 font-sans">
              Join thousands of professionals who found their dream jobs with CareerMatch AI
            </p>
          </div>

          <Card className="border-0 shadow-xl">
            <CardContent className="p-8">
              <div className="flex items-center justify-between mb-6">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={prevTestimonial}
                  className="h-10 w-10 rounded-full bg-white shadow-md hover:shadow-lg"
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <div className="flex space-x-2">
                  {testimonials.map((_, index) => (
                    <div
                      key={index}
                      className={`w-2 h-2 rounded-full ${
                        index === currentTestimonial ? "bg-purple-600" : "bg-gray-300"
                      }`}
                    />
                  ))}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={nextTestimonial}
                  className="h-10 w-10 rounded-full bg-white shadow-md hover:shadow-lg"
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>

              <div className="text-center">
                <Quote className="h-8 w-8 text-purple-600 mx-auto mb-4" />
                <blockquote className="text-xl text-gray-700 mb-6 font-sans leading-relaxed">
                  "{testimonials[currentTestimonial].content}"
                </blockquote>
                <div className="flex justify-center mb-4">
                  {[...Array(testimonials[currentTestimonial].rating)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <div>
                  <div className="font-semibold text-gray-800 font-sans">{testimonials[currentTestimonial].name}</div>
                  <div className="text-gray-600 font-sans">
                    {testimonials[currentTestimonial].role} at {testimonials[currentTestimonial].company}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-purple-600 to-purple-800">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-4xl font-bold text-white mb-4 font-sans">Ready to Transform Your Career?</h2>
          <p className="text-xl text-purple-100 mb-8 font-sans">
            Join thousands of professionals who have accelerated their careers with AI-powered job matching
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/upload">
              <Button size="lg" className="bg-white text-purple-600 hover:bg-gray-100 px-8 py-4 text-lg font-sans">
                Upload Your CV Now
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/jobs">
              <Button
                size="lg"
                variant="outline"
                className="border-white text-white hover:bg-white hover:text-purple-600 px-8 py-4 text-lg font-sans bg-transparent"
              >
                Explore Jobs
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 bg-gray-900 text-white">
        <div className="container mx-auto max-w-6xl">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Brain className="h-6 w-6 text-purple-400" />
                <span className="text-lg font-bold font-sans">CareerMatch AI</span>
              </div>
              <p className="text-gray-400 font-sans">
                AI-powered career matching platform helping professionals find their dream jobs.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4 font-sans">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link href="/upload" className="hover:text-white font-sans">
                    CV Upload
                  </Link>
                </li>
                <li>
                  <Link href="/jobs" className="hover:text-white font-sans">
                    Job Search
                  </Link>
                </li>
                <li>
                  <a href="#" className="hover:text-white font-sans">
                    API
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4 font-sans">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <a href="#" className="hover:text-white font-sans">
                    About
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white font-sans">
                    Careers
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white font-sans">
                    Contact
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4 font-sans">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <a href="#" className="hover:text-white font-sans">
                    Help Center
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white font-sans">
                    Privacy Policy
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white font-sans">
                    Terms of Service
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p className="font-sans">© 2024 CareerMatch AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
