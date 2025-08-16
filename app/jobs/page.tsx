"use client"
// Update the import path to the correct relative location
import { JobMatchingDashboard } from "../../components/job-matching-dashboard";

export default function JobsPage() {
  return (
    <main className="min-h-screen bg-background">
      <JobMatchingDashboard />
    </main>
  )
}
