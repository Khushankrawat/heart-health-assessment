import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatRiskScore(score: number): string {
  return (score * 100).toFixed(1) + '%'
}

export function getRiskColor(riskLevel: string): string {
  switch (riskLevel.toLowerCase()) {
    case 'low':
      return 'text-green-600 bg-green-50'
    case 'moderate':
      return 'text-yellow-600 bg-yellow-50'
    case 'high':
      return 'text-red-600 bg-red-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

export function getRiskIcon(riskLevel: string): string {
  switch (riskLevel.toLowerCase()) {
    case 'low':
      return '✅'
    case 'moderate':
      return '⚠️'
    case 'high':
      return '🚨'
    default:
      return '❓'
  }
}
