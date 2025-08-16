"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge"
import { Input } from "../components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select"
import { Alert, AlertDescription } from "../components/ui/alert"
import Link from "next/link"
import {
  Search,
  MapPin,
  Building2,
  DollarSign,
  Star,
  TrendingUp,
  Users,
  Briefcase,
  ExternalLink,
  SortDesc,
  ChevronLeft,
} from "lucide-react"
// import { cn } from "../../lib/utils";

interface JobMatch {
  job_id: number
  score: number
  reasons?: {
    overlap_skills: string[]
    missing_skills: string[]
    loc_job: string
    loc_cand: string[]
    score_hint: number
  }
  title: string
  description: string
  company_norm: string
  location_norm: string
  experience_level: string
  job_type: string
  industry: string
  skills_norm: string[]
  salary_min_vnd?: number
  salary_max_vnd?: number
  salary_currency?: string
  date_posted?: string
  external_link?: string
}

interface JobMatchingDashboardProps {
  candidateId?: string
}

const normalizeJob = (job: any): JobMatch => {
  const reasons = job?.reasons || {}
  return {
    job_id: Number(job.job_id ?? 0),
    score: Number(job.score ?? 0),
    reasons: {
      overlap_skills: Array.isArray(reasons.overlap_skills) ? reasons.overlap_skills : [],
      missing_skills: Array.isArray(reasons.missing_skills) ? reasons.missing_skills : [],
      loc_job: reasons.loc_job ?? job.location_norm ?? "",
      loc_cand: Array.isArray(reasons.loc_cand) ? reasons.loc_cand : [],
      score_hint: Number(reasons.score_hint ?? job.score ?? 0),
    },
    title: String(job.title ?? ""),
    description: String(job.description ?? ""),
    company_norm: String(job.company_norm ?? ""),
    location_norm: String(job.location_norm ?? ""),
    experience_level: String(job.experience_level ?? ""),
    job_type: String(job.job_type ?? ""),
    industry: String(job.industry ?? ""),
    skills_norm: Array.isArray(job.skills_norm) ? job.skills_norm : [],
    salary_min_vnd: job.salary_min_vnd ?? undefined,
    salary_max_vnd: job.salary_max_vnd ?? undefined,
    salary_currency: job.salary_currency ?? "VND",
    date_posted: job.date_posted ?? undefined,
    external_link: job.external_link ?? undefined,
  }
}

// Thêm hàm lấy danh sách ứng viên
async function fetchCandidates() {
  const res = await fetch("/candidates", { method: "GET" })
  return await res.json()
}

export function JobMatchingDashboard({ candidateId, initialKeyword }: JobMatchingDashboardProps & { initialKeyword?: string }) {
  const [jobs, setJobs] = useState<JobMatch[]>([]);
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("");
  const [searchKeyword, setSearchKeyword] = useState(initialKeyword ?? "");
  const [sortBy, setSortBy] = useState<"score" | "date" | "salary">("score")
  const [filterLocation, setFilterLocation] = useState("all")
  const [filterExperience, setFilterExperience] = useState("all")
  const [selectedJob, setSelectedJob] = useState<JobMatch | null>(null)

  // Chỉ fetch API ở client
  const API_BASE = typeof window !== "undefined" ? (process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000") : "";
  const searchJobs = async (keyword?: string) => {
    if (typeof window === "undefined") return;
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/search/jobs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          cand_id: candidateId ?? null,
          keyword: keyword ?? null,
          top_k: 10,
        }),
      });
      let jobMatches: JobMatch[] = [];
      if (response.headers.get("content-type")?.includes("application/json")) {
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Search failed: ${response.statusText}`);
        }
        jobMatches = await response.json();
      } else {
        const text = await response.text();
        throw new Error(text || `Search failed: ${response.statusText}`);
      }
      const normalized = (jobMatches || []).map(normalizeJob);
      setJobs(normalized);
      if (normalized.length > 0 && !selectedJob) setSelectedJob(normalizeJob(normalized[0]));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to search jobs. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Chỉ fetch ở client
    if (typeof window !== "undefined") {
      searchJobs(searchKeyword);
    }
  }, [candidateId]);
  const handleSearch = () => {
    searchJobs(searchKeyword);
  }
  const getReasons = (job: JobMatch | null) => ({
    overlap_skills: job?.reasons?.overlap_skills ?? [],
    missing_skills: job?.reasons?.missing_skills ?? [],
    loc_job: job?.reasons?.loc_job ?? job?.location_norm ?? "",
    loc_cand: job?.reasons?.loc_cand ?? [],
    score_hint: job?.reasons?.score_hint ?? job?.score ?? 0,
  })

  // No search bar, jobs are fetched automatically

  const formatSalary = (min?: number, max?: number, currency = "VND") => {
    if (!min && !max) return "Negotiable";

    const formatAmount = (amount: number) => {
      if (currency === "VND") {
        return `${(amount / 1000000).toFixed(0)}M VND`;
      }
      return `${amount.toLocaleString()} ${currency}`;
    };

    if (min && max) {
      return `${formatAmount(min)} - ${formatAmount(max)}`;
    }
    return formatAmount(min || max || 0);
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return "text-green-600 bg-green-100"
    if (score >= 0.6) return "text-yellow-600 bg-yellow-100"
    return "text-red-600 bg-red-100"
  }

  const getScoreLabel = (score: number) => {
    if (score >= 0.8) return "Excellent Match"
    if (score >= 0.6) return "Good Match"
    return "Fair Match"
  }

  const filteredAndSortedJobs = jobs
    .filter((job) => {
      // Chỉ lọc theo location nếu người dùng chọn khác 'all'
      if (filterLocation && filterLocation.toLowerCase() !== "all") {
        if (!job.location_norm?.toLowerCase().includes(filterLocation.toLowerCase())) {
          return false;
        }
      }
      // Chỉ lọc theo experience nếu người dùng chọn khác 'all'
      if (filterExperience && filterExperience.toLowerCase() !== "all") {
        if (job.experience_level?.toLowerCase() !== filterExperience.toLowerCase()) {
          return false;
        }
      }
      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case "score":
          return b.score - a.score;
        case "date":
          return new Date(b.date_posted || 0).getTime() - new Date(a.date_posted || 0).getTime();
        case "salary":
          return (b.salary_max_vnd || 0) - (a.salary_max_vnd || 0);
        default:
          return 0;
      }
    });

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Back to Home link - more prominent */}
      <div className="mb-6 flex items-center">
        <Link href="/" className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-50 hover:bg-purple-100 text-purple-700 font-semibold font-sans shadow-sm transition">
          <ChevronLeft className="h-5 w-5" />
          <span>Back to Home</span>
        </Link>
      </div>

      {/* Header - visually improved */}
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-extrabold text-cyan-900 mb-3 font-sans tracking-tight drop-shadow-sm">Job Matching Dashboard</h1>
        <p className="text-lg text-muted-foreground font-sans">
          {candidateId
            ? "Here are jobs matched to your profile. Refine your search below to find the best fit!"
            : "Search for jobs that match your skills and preferences. Enter keywords to get started!"}
        </p>
      </div>

      {/* Search and Filters */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                  <Input
                    placeholder="Search jobs by keywords..."
                    value={searchKeyword}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchKeyword(e.target.value)}
                    className="pl-10 font-sans"
                    onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === "Enter" && handleSearch()}
                  />
                </div>
                <Button
                  onClick={handleSearch}
                  className="bg-cyan-500 hover:bg-cyan-700 text-white font-sans shadow-md border-none rounded-lg px-6 py-2"
                >
                  Search
                </Button>
              </div>
            </div>

            {/* Filters */}
            <div className="flex gap-2">
              <Select value={filterLocation} onValueChange={setFilterLocation}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Location" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Locations</SelectItem>
                  <SelectItem value="hanoi">Hanoi</SelectItem>
                  <SelectItem value="ho chi minh city">Ho Chi Minh City</SelectItem>
                  <SelectItem value="da nang">Da Nang</SelectItem>
                </SelectContent>
              </Select>

              <Select value={filterExperience} onValueChange={setFilterExperience}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Experience" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Experience</SelectItem>
                  <SelectItem value="mid">Mid-level</SelectItem>
                  <SelectItem value="senior">Senior</SelectItem>
                  <SelectItem value="lead">Lead</SelectItem>
                </SelectContent>
              </Select>

              <Select value={sortBy} onValueChange={(value: "score" | "date" | "salary") => setSortBy(value)}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="score">By Score</SelectItem>
                  <SelectItem value="date">By Date</SelectItem>
                  <SelectItem value="salary">By Salary</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error State */}
      {error && (
        <Alert className="mb-6 border-red-200 bg-red-50">
          <AlertDescription className="text-red-800 font-sans">{error}</AlertDescription>
        </Alert>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto mb-4"></div>
          <p className="text-muted-foreground font-sans">Searching for matching jobs...</p>
        </div>
      )}

      {/* Results */}
      {!loading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Job List */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold font-sans">{filteredAndSortedJobs.length} Jobs Found</h2>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <SortDesc className="h-4 w-4" />
                <span className="font-sans">Sorted by {sortBy}</span>
              </div>
            </div>

            {filteredAndSortedJobs.map((job) => (
              <Card
                key={job.job_id}
                className={`cursor-pointer transition-all hover:shadow-md ${
                  selectedJob?.job_id === job.job_id ? "ring-2 ring-cyan-500" : ""
                }`}
                onClick={() => setSelectedJob(job)}
              >
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg mb-1 font-sans">{job.title}</h3>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground mb-2">
                        <div className="flex items-center gap-1">
                          <Building2 className="h-4 w-4" />
                          <span className="font-sans">{job.company_norm}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <MapPin className="h-4 w-4" />
                          <span className="font-sans">{job.location_norm}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge className={`${getScoreColor(job.score)} font-sans`}>
                        <Star className="h-3 w-3 mr-1" />
                        {(job.score * 100).toFixed(0)}%
                      </Badge>
                      <p className="text-xs text-muted-foreground mt-1 font-sans">{getScoreLabel(job.score)}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-muted-foreground mb-3">
                    <div className="flex items-center gap-1">
                      <Briefcase className="h-4 w-4" />
                      <span className="font-sans">{job.experience_level}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Users className="h-4 w-4" />
                      <span className="font-sans">{job.job_type}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <DollarSign className="h-4 w-4" />
                      <span className="font-sans">{formatSalary(job.salary_min_vnd, job.salary_max_vnd)}</span>
                    </div>
                  </div>

                  {/* Matching Skills Preview */}
                  {Array.isArray(job.reasons?.overlap_skills) && job.reasons.overlap_skills.length > 0 && (
                    <div className="mb-3">
                      <p className="text-sm font-medium mb-1 font-sans">Matching Skills:</p>
                      <div className="flex flex-wrap gap-1">
                        {job.reasons.overlap_skills.slice(0, 3).map((skill, index) => (
                          <Badge key={skill + '-' + index} variant="secondary" className="text-xs font-sans">
                            {skill}
                          </Badge>
                        ))}
                        {job.reasons.overlap_skills.length > 3 && (
                          <Badge variant="secondary" className="text-xs font-sans">
                            +{job.reasons.overlap_skills.length - 3} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}

                  <p className="text-sm text-muted-foreground line-clamp-2 font-sans">{job.description}</p>
                </CardContent>
              </Card>
            ))}

            {filteredAndSortedJobs.length === 0 && !loading && (
              <div className="text-center py-12">
                <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2 font-sans">No jobs found</h3>
                <p className="text-muted-foreground font-sans">Try adjusting your search criteria or filters</p>
              </div>
            )}
          </div>

          {/* Job Details */}
          <div className="lg:sticky lg:top-4">
            {selectedJob ? (
              (() => {
                const r = getReasons(selectedJob)
                return (
                  <Card>
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="font-sans">{selectedJob.title}</CardTitle>
                          <CardDescription className="font-sans">
                            {selectedJob.company_norm} • {selectedJob.location_norm}
                          </CardDescription>
                        </div>
                        <Badge className={`${getScoreColor(selectedJob.score)} font-sans`}>
                          {(selectedJob.score * 100).toFixed(0)}% Match
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {/* Job Info */}
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <h4 className="font-semibold text-sm text-muted-foreground mb-1 font-sans">Experience Level</h4>
                          <p className="font-sans">{selectedJob.experience_level}</p>
                        </div>
                        <div>
                          <h4 className="font-semibold text-sm text-muted-foreground mb-1 font-sans">Job Type</h4>
                          <p className="font-sans">{selectedJob.job_type}</p>
                        </div>
                        <div>
                          <h4 className="font-semibold text-sm text-muted-foreground mb-1 font-sans">Industry</h4>
                          <p className="font-sans">{selectedJob.industry}</p>
                        </div>
                        <div>
                          <h4 className="font-semibold text-sm text-muted-foreground mb-1 font-sans">Salary</h4>
                          <p className="font-sans">
                            {formatSalary(selectedJob.salary_min_vnd, selectedJob.salary_max_vnd)}
                          </p>
                        </div>
                      </div>

                      {/* Matching Analysis */}
                      <div>
                        <h4 className="font-semibold mb-3 flex items-center gap-2 font-sans">
                          <TrendingUp className="h-4 w-4 text-cyan-600" />
                          Why This Job Matches You
                        </h4>

                        {r.overlap_skills.length > 0 && (
                          <div className="mb-4">
                            <h5 className="font-medium text-sm text-green-700 mb-2 font-sans">
                              ✓ Skills You Have ({r.overlap_skills.length})
                            </h5>
                            <div className="flex flex-wrap gap-1">
                              {r.overlap_skills.map((skill, index) => (
                                <Badge key={skill + '-' + index} className="bg-green-100 text-green-800 font-sans">
                                  {skill}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}

                        {r.missing_skills.length > 0 && (
                          <div className="mb-4">
                            <h5 className="font-medium text-sm text-orange-700 mb-2 font-sans">
                              ⚠ Skills to Develop ({r.missing_skills.length})
                            </h5>
                            <div className="flex flex-wrap gap-1">
                              {r.missing_skills.slice(0, 5).map((skill, index) => (
                                <Badge
                                  key={skill + '-' + index}
                                  variant="outline"
                                  className="text-orange-700 border-orange-300 font-sans"
                                >
                                  {skill}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Required Skills */}
                      {selectedJob.skills_norm.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-sm text-muted-foreground mb-2 font-sans">Required Skills</h4>
                          <div className="flex flex-wrap gap-1">
                            {selectedJob.skills_norm.map((skill, index) => (
                              <Badge key={skill + '-' + index} variant="secondary" className="font-sans">
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Description */}
                      <div>
                        <h4 className="font-semibold text-sm text-muted-foreground mb-2 font-sans">Job Description</h4>
                        <p className="text-sm leading-relaxed font-sans">{selectedJob.description}</p>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-3">
                        <Button className="flex-1 bg-green-400 hover:bg-green-600 text-white font-sans border-none rounded-lg px-6 py-2">Apply Now</Button>
                        {selectedJob.external_link && (
                          <Button
                            variant="outline"
                            asChild
                            className="font-sans bg-purple-200 hover:bg-purple-400 text-purple-900 border-none rounded-lg px-6 py-2"
                          >
                            <a href={selectedJob.external_link} target="_blank" rel="noopener noreferrer">
                              <ExternalLink className="h-4 w-4 mr-2" />
                              View Original
                            </a>
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )
              })()
            ) : (
              <Card>
                <CardContent className="p-12 text-center">
                  <Briefcase className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2 font-sans">Select a Job</h3>
                  <p className="text-muted-foreground font-sans">
                    Click on a job from the list to see detailed information and matching analysis
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
