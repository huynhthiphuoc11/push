"use client"

import React, { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Badge } from "../components/ui/badge"
import { Progress } from "../components/ui/progress"
import { Alert, AlertDescription } from "../components/ui/alert"
import Link from "next/link"
import { ChevronLeft } from "lucide-react"
import {
  Upload,
  FileText,
  CheckCircle,
  AlertCircle,
  User,
  Mail,
  Phone,
  MapPin,
  Briefcase,
  GraduationCap,
} from "lucide-react"
import { JobMatchingDashboard } from "./job-matching-dashboard"

interface CandidateInfo {
  cand_id: string
  name: string
  emails: string[]
  phones: string[]
  locations: string[]
  skills_norm: string[]
  exp_years: number
  experience_entries: string[]
  education_entries: string[]
}

interface UploadResponse {
  success: boolean
  message: string
  candidate?: CandidateInfo
  error?: string
}

export function CVUploadInterface() {
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle")
  const [uploadProgress, setUploadProgress] = useState(0)
  const [parsedData, setParsedData] = useState<CandidateInfo | null>(null)
  const [errorMessage, setErrorMessage] = useState("")
  const [showKeywordPrompt, setShowKeywordPrompt] = useState(false)
  const [searchKeyword, setSearchKeyword] = useState("");
  const [startMatching, setStartMatching] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(false);

  const validateFile = (file: File): string | null => {
    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "text/plain",
    ]

    if (!allowedTypes.includes(file.type)) {
      return "Invalid file type. Please upload a PDF, DOCX, or TXT file."
    }

    if (file.size > 10 * 1024 * 1024) {
      return "File too large. Maximum size is 10MB."
    }

    if (file.size < 100) {
      return "File too small. Please upload a valid CV file."
    }

    return null
  }

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    const validationError = validateFile(file)
    if (validationError) {
      setUploadStatus("error")
      setErrorMessage(validationError)
      return
    }

    setUploadStatus("uploading")
    setUploadProgress(0)
    setErrorMessage("")

    try {
      const formData = new FormData()
      formData.append("file", file)

      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 85) {
            clearInterval(progressInterval)
            return 85
          }
          return prev + Math.random() * 15
        })
      }, 300)

      const res = await fetch(`${API_BASE}/candidates/upload`, { method: "POST", body: formData });
      let data;
      try {
        if (res.headers.get("content-type")?.includes("application/json")) {
          data = await res.json();
        } else {
          const text = await res.text();
          throw new Error(text || "Upload failed");
        }
      } catch (err) {
        clearInterval(progressInterval);
        setUploadStatus("error");
        setErrorMessage(err instanceof Error ? err.message : "Upload failed");
        return;
      }
      clearInterval(progressInterval);
      setUploadProgress(100);
      if (res.ok && data.success && data.candidate) {
        setUploadStatus("success");
        setParsedData(data.candidate);
      } else {
        setUploadStatus("error");
        setErrorMessage(data.error || data.detail || res.statusText || "Upload failed");
      }
    } catch (error) {
      setUploadStatus("error")
      setErrorMessage(error instanceof Error ? error.message : "Network error. Please check your connection.")
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/plain": [".txt"],
    },
    multiple: false,
  })

  const resetUpload = () => {
    setUploadStatus("idle")
    setUploadProgress(0)
    setParsedData(null)
    setErrorMessage("")
    setShowKeywordPrompt(false)
    setSearchKeyword("")
    setStartMatching(false)
    setShowAnalysis(false)
  }

  // After successful upload, show keyword prompt before dashboard
  const handleFindJobs = () => {
    setShowKeywordPrompt(true)
  }

  // Skeleton loader for dashboard
  function DashboardSkeleton() {
    return (
      <div className="mt-10">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-1/3 mx-auto" />
          <div className="h-6 bg-muted rounded w-1/2 mx-auto" />
          <div className="h-96 bg-muted rounded w-full" />
        </div>
      </div>
    )
  }

  // Show keyword prompt after upload
  // Skip keyword prompt, go directly to dashboard after upload
  if (showKeywordPrompt && parsedData && parsedData.cand_id) {
    // Use React Suspense for async loading
    return (
      <React.Suspense fallback={<DashboardSkeleton />}>
        <JobMatchingDashboard candidateId={parsedData.cand_id} />
      </React.Suspense>
    );
  }

  // Show job matching dashboard after keyword entered
  if (showKeywordPrompt && parsedData && parsedData.cand_id && startMatching) {
    return <JobMatchingDashboard candidateId={parsedData.cand_id} initialKeyword={searchKeyword} />;
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-6">
        <Link href="/" className="text-purple-600 hover:text-purple-700 font-sans flex items-center gap-2">
          <ChevronLeft className="h-4 w-4" />
          Back to Home
        </Link>
      </div>

      {/* Header - visually improved */}
      <div className="text-center mb-8">
        <h1 className="text-5xl font-extrabold text-cyan-900 mb-4 font-sans tracking-tight drop-shadow-sm">
          Upload Your CV & Unlock New Opportunities
        </h1>
        <p className="text-xl text-cyan-700 font-sans mb-2">
          Let AI analyze your CV and match you with the perfect jobs for your skills and experience.
        </p>
      </div>

      {/* Upload Area */}
      {uploadStatus === "idle" && (
        <Card className="mb-8">
          <CardContent className="p-8">
            <div
              {...getRootProps()}
              className={`
                border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all duration-200
                ${
                  isDragActive
                    ? "border-cyan-500 bg-cyan-50 scale-105"
                    : "border-border hover:border-cyan-400 hover:bg-cyan-50/50"
                }
              `}
            >
              <input {...getInputProps()} />
              <Upload className="mx-auto h-12 w-12 text-cyan-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2 font-sans">
                {isDragActive ? "Drop your CV here" : "Drag & drop your CV here or click to browse"}
              </h3>
              <p className="text-muted-foreground mb-4 font-sans">Supported formats: PDF, DOCX, TXT (Max 10MB)</p>
              <Button className="bg-cyan-800 hover:bg-cyan-700 text-white">
                <FileText className="mr-2 h-4 w-4" />
                Choose File
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Upload Progress */}
      {uploadStatus === "uploading" && (
        <Card className="mb-8">
          <CardContent className="p-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto mb-4"></div>
              <h3 className="text-xl font-semibold mb-4 font-sans">Analyzing your CV, please wait...</h3>
              <Progress value={uploadProgress} className="w-full mb-2" />
              <p className="text-sm text-muted-foreground font-sans">{uploadProgress}% complete</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {uploadStatus === "error" && (
        <Alert className="mb-8 border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800 font-sans">{errorMessage}</AlertDescription>
        </Alert>
      )}

      {/* Success State with Parsed Results */}
      {uploadStatus === "success" && parsedData && (
        <div className="space-y-6">
          {/* Success Message */}
          <Alert className="border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800 font-sans">
              CV uploaded and analyzed successfully! Here's what we found:
            </AlertDescription>
          </Alert>

          {/* Candidate Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-sans">
                <User className="h-5 w-5 text-cyan-600" />
                Personal Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-sm text-muted-foreground mb-1 font-sans">Name</h4>
                  <p className="font-sans">{parsedData.name}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-sm text-muted-foreground mb-1 font-sans">Experience</h4>
                  <p className="font-sans">{parsedData.exp_years} years</p>
                </div>
              </div>

              {parsedData.emails.length > 0 && (
                <div>
                  <h4 className="font-semibold text-sm text-muted-foreground mb-2 flex items-center gap-1 font-sans">
                    <Mail className="h-4 w-4" />
                    Email
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {parsedData.emails.map((email, index) => (
                      <Badge key={index} variant="secondary" className="font-sans">
                        {email}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {parsedData.phones.length > 0 && (
                <div>
                  <h4 className="font-semibold text-sm text-muted-foreground mb-2 flex items-center gap-1 font-sans">
                    <Phone className="h-4 w-4" />
                    Phone
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {parsedData.phones.map((phone, index) => (
                      <Badge key={index} variant="secondary" className="font-sans">
                        {phone}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {parsedData.locations.length > 0 && (
                <div>
                  <h4 className="font-semibold text-sm text-muted-foreground mb-2 flex items-center gap-1 font-sans">
                    <MapPin className="h-4 w-4" />
                    Location
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {parsedData.locations.map((location, index) => (
                      <Badge key={index} variant="secondary" className="font-sans">
                        {location}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Skills */}
          {parsedData.skills_norm.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="font-sans">Technical Skills</CardTitle>
                <CardDescription className="font-sans">
                  We identified {parsedData.skills_norm.length} key skills from your CV
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {parsedData.skills_norm.map((skill, index) => (
                    <Badge key={index} className="bg-cyan-100 text-cyan-800 hover:bg-cyan-200 font-sans">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Experience */}
          {parsedData.experience_entries.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 font-sans">
                  <Briefcase className="h-5 w-5 text-cyan-600" />
                  Work Experience
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {parsedData.experience_entries.map((experience, index) => (
                    <div key={index} className="p-3 bg-muted rounded-lg">
                      <p className="font-sans">{experience}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Education */}
          {parsedData.education_entries.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 font-sans">
                  <GraduationCap className="h-5 w-5 text-cyan-600" />
                  Education
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {parsedData.education_entries.map((education, index) => (
                    <div key={index} className="p-3 bg-muted rounded-lg">
                      <p className="font-sans">{education}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Action Buttons & Analyze CV (link to new page) */}
          <div className="flex gap-4 justify-center">
            <Button onClick={resetUpload} variant="outline" className="font-sans bg-transparent">
              Upload Another CV
            </Button>
            <Button onClick={handleFindJobs} className="bg-cyan-800 hover:bg-cyan-700 text-white font-sans">
              <Link href="/jobs" passHref legacyBehavior>
                <a className="bg-cyan-800 hover:bg-cyan-700 text-white font-sans px-4 py-2 rounded inline-block">
                  Find Matching Jobs
                </a>
              </Link>
            </Button>
            <Link href={parsedData?.cand_id ? `/cv-analysis?id=${parsedData.cand_id}` : "#"} passHref legacyBehavior>
              <a>
                <Button className="bg-purple-700 hover:bg-purple-800 text-white font-sans">
                  Analyze CV
                </Button>
              </a>
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
