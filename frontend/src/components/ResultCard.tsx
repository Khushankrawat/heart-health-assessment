import { motion } from 'framer-motion'
import { Heart, TrendingUp, AlertTriangle, CheckCircle, RotateCcw, Stethoscope, Activity } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { formatRiskScore, getRiskColor, getRiskIcon } from '@/lib/utils'
import type { HeartDiseasePrediction } from '@/lib/api'

interface ResultCardProps {
  prediction: HeartDiseasePrediction
  onReset: () => void
}

export function ResultCard({ prediction, onReset }: ResultCardProps) {
  const riskScore = prediction.risk_score
  const riskLevel = prediction.risk_level
  const riskPercentage = riskScore * 100


  const getRiskDescription = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low':
        return 'Your risk of heart disease is relatively low. Continue maintaining a healthy lifestyle.'
      case 'moderate':
        return 'Your risk of heart disease is moderate. Consider lifestyle changes and regular health checkups.'
      case 'high':
        return 'Your risk of heart disease is high. Please consult a healthcare professional immediately.'
      default:
        return 'Risk assessment completed.'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, type: "spring" }}
    >
      <Card className="w-full max-w-4xl mx-auto shadow-xl hover:shadow-2xl transition-shadow duration-300">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <motion.div
              animate={{ rotate: [0, 5, -5, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Stethoscope className="h-5 w-5 text-blue-600" />
            </motion.div>
            Cardiovascular Risk Assessment
            <motion.div
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <Activity className="h-4 w-4 text-green-500" />
            </motion.div>
          </CardTitle>
          <CardDescription>
            Professional cardiovascular risk evaluation using advanced AI analysis
          </CardDescription>
        </CardHeader>
      <CardContent className="space-y-6">
        {/* Risk Score Display */}
        <motion.div 
          className="text-center space-y-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <motion.div 
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-lg font-semibold ${getRiskColor(riskLevel)}`}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.4, type: "spring" }}
          >
            <motion.span 
              className="text-2xl"
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              {getRiskIcon(riskLevel)}
            </motion.span>
            {riskLevel} Risk
          </motion.div>
          
          <motion.div 
            className="space-y-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            <div className="text-3xl font-bold">{formatRiskScore(riskScore)}</div>
            <div className="text-sm text-muted-foreground">Probability of Heart Disease</div>
          </motion.div>

          <motion.div 
            className="w-full max-w-md mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
          >
            <Progress value={riskPercentage} className="h-3" />
            <div className="flex justify-between text-xs text-muted-foreground mt-1">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </motion.div>

          <motion.p 
            className="text-sm text-muted-foreground max-w-md mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.0 }}
          >
            {getRiskDescription(riskLevel)}
          </motion.p>
        </motion.div>

        {/* Top Contributing Factors */}
        <motion.div 
          className="space-y-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2 }}
        >
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <motion.div
              animate={{ rotate: [0, 5, -5, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <TrendingUp className="h-4 w-4 text-blue-600" />
            </motion.div>
            Top Contributing Factors
          </h3>
          <div className="grid gap-3">
            {prediction.top_contributors.map((contributor: any, index: number) => (
              <motion.div 
                key={contributor.feature} 
                className="flex items-center justify-between p-3 bg-muted/50 rounded-lg hover:bg-muted/70 transition-colors"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.4 + index * 0.1 }}
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center gap-3">
                  <motion.div 
                    className="flex items-center justify-center w-6 h-6 bg-primary text-primary-foreground rounded-full text-xs font-semibold"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 1.6 + index * 0.1, type: "spring" }}
                  >
                    {index + 1}
                  </motion.div>
                  <div>
                    <div className="font-medium capitalize">
                      {contributor.feature.replace(/_/g, ' ')}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Value: {contributor.value}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">
                    {contributor.importance.toFixed(1)}%
                  </div>
                  <div className="text-xs text-muted-foreground">Importance</div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Educational Notes */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            Health Recommendations
          </h3>
          <div className="space-y-2">
            {prediction.notes.map((note: string, index: number) => (
              <div key={index} className="flex items-start gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-blue-800">{note}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Model Information */}
        <div className="pt-4 border-t">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>Model Version: {prediction.model_version}</span>
            <span>Generated: {new Date().toLocaleString()}</span>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-yellow-800">
              <p className="font-medium">Important Disclaimer</p>
              <p className="mt-1">
                This tool is for educational use only and not for medical diagnosis. 
                Always consult a qualified healthcare professional for any health concerns.
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <motion.div 
          className="flex gap-3 pt-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.0 }}
        >
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex-1"
          >
            <Button onClick={onReset} variant="outline" className="w-full">
              <RotateCcw className="h-4 w-4 mr-2" />
              Start New Assessment
            </Button>
          </motion.div>
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex-1"
          >
            <Button 
              onClick={() => window.print()} 
              variant="secondary" 
              className="w-full"
            >
              <Zap className="h-4 w-4 mr-2" />
              Print Results
            </Button>
          </motion.div>
        </motion.div>
      </CardContent>
    </Card>
    </motion.div>
  )
}
