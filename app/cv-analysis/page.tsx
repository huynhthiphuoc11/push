
"use client";
import React, { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { FileText, CheckCircle, AlertCircle, User, Mail, Phone, MapPin, Briefcase, GraduationCap } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/card";

interface CandidateInfo {
  cand_id: string;
  name: string;
  emails: string[];
  phones: string[];
  locations: string[];
  skills_norm: string[];
  exp_years: number;
  experience_entries: string[];
  education_entries: string[];
}

function CVAnalysisContent() {
  const searchParams = useSearchParams();
  const candidateId = searchParams.get("id");
  const [parsedData, setParsedData] = useState<CandidateInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchCandidate() {
      if (!candidateId) return;
      try {
        // Gọi API backend để lấy dữ liệu ứng viên
        const res = await fetch(`/api/candidates/${candidateId}`);
        if (res.ok) {
          const data = await res.json();
          setParsedData(data);
        } else {
          setParsedData(null);
        }
      } catch {
        setParsedData(null);
      }
      setLoading(false);
    }
    fetchCandidate();
  }, [candidateId]);

  function calculateScore(data: CandidateInfo | null): number {
    if (!data) return 0;
    let score = 0;
    score += Math.min(data.skills_norm.length * 6, 60);
    score += Math.min(data.exp_years * 5, 25);
    score += Math.min(data.education_entries.length * 5, 15);
    return Math.min(score, 100);
  }

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-xl text-gray-500">Loading CV analysis...</div>;
  }
  if (!parsedData) {
    return <div className="min-h-screen flex items-center justify-center text-xl text-red-500">Candidate not found or error loading data.</div>;
  }

  const score = calculateScore(parsedData);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-100 py-16 px-4 flex justify-center items-start">
      <Card className="border-2 border-purple-300 shadow-xl w-full max-w-2xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-3 font-sans text-purple-800 text-2xl">
            <FileText className="h-7 w-7 text-purple-600" />
            CV Analysis & Improvement Suggestions
          </CardTitle>
          <CardDescription className="text-gray-600 font-sans text-base mt-2">
            Get a professional review of your CV and actionable tips to boost your career prospects.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Thông tin ứng viên */}
          <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="flex items-center gap-2 mb-2 text-cyan-700 font-bold"><User className="h-5 w-5" /> Name:</div>
              <div className="text-gray-800 font-sans">{parsedData.name}</div>
              <div className="flex items-center gap-2 mt-2 text-cyan-700 font-bold"><Mail className="h-5 w-5" /> Email:</div>
              <div className="text-gray-800 font-sans">{parsedData.emails?.join(", ")}</div>
              <div className="flex items-center gap-2 mt-2 text-cyan-700 font-bold"><Phone className="h-5 w-5" /> Phone:</div>
              <div className="text-gray-800 font-sans">{parsedData.phones?.join(", ")}</div>
              <div className="flex items-center gap-2 mt-2 text-cyan-700 font-bold"><MapPin className="h-5 w-5" /> Location:</div>
              <div className="text-gray-800 font-sans">{parsedData.locations?.join(", ")}</div>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-2 text-cyan-700 font-bold"><Briefcase className="h-5 w-5" /> Experience:</div>
              <div className="text-gray-800 font-sans">{parsedData.exp_years} years</div>
              <div className="flex items-center gap-2 mt-2 text-cyan-700 font-bold"><GraduationCap className="h-5 w-5" /> Education:</div>
              <div className="text-gray-800 font-sans">{parsedData.education_entries?.join(", ")}</div>
            </div>
          </div>
          {/* Điểm số & phân tích */}
          <div className="mb-6 flex flex-col items-center">
            <span className="font-bold text-lg text-purple-700 mb-2">CV Score</span>
            <div className="w-full max-w-xs">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm text-gray-500">0</span>
                <span className="flex-1" />
                <span className="text-sm text-gray-700">100</span>
              </div>
              <div className="relative h-6 bg-purple-100 rounded-full overflow-hidden">
                <div
                  className="absolute left-0 top-0 h-full bg-gradient-to-r from-purple-500 to-purple-700"
                  style={{ width: `${score}%` }}
                />
                <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-purple-900 font-bold text-lg">
                  {score} / 100
                </span>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-6">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="font-semibold text-green-700">Strengths</span>
              </div>
              <ul className="list-disc pl-6 text-green-900 text-base">
                {parsedData.skills_norm.length > 5 && <li>Strong technical skill set</li>}
                {parsedData.exp_years > 3 && <li>Solid work experience</li>}
                {parsedData.education_entries.length > 0 && <li>Good education background</li>}
                {parsedData.skills_norm.length > 10 && <li>Versatile skill profile</li>}
                {parsedData.exp_years > 7 && <li>Senior-level experience</li>}
                {parsedData.education_entries.length > 2 && <li>Diverse education history</li>}
              </ul>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <span className="font-semibold text-red-700">Suggestions for Improvement</span>
              </div>
              <ul className="list-disc pl-6 text-red-900 text-base">
                {parsedData.skills_norm.length < 5 && <li>Add more relevant technical skills</li>}
                {parsedData.exp_years < 2 && <li>Highlight internships or projects to show experience</li>}
                {parsedData.education_entries.length === 0 && <li>Include your education details</li>}
                <li>Make sure your CV is clear, concise, and tailored for the jobs you want</li>
                <li>Use action verbs and quantify achievements</li>
                <li>Keep formatting clean and professional</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function CVAnalysisPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-xl text-gray-500">Loading CV analysis...</div>}>
      <CVAnalysisContent />
    </Suspense>
  );
}
