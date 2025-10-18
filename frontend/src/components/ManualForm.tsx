import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Heart, User, Activity, ClipboardList } from 'lucide-react'
import type { HeartDiseaseInput } from '@/lib/api.ts'

interface ManualFormProps {
  onSubmit: (data: HeartDiseaseInput) => void
  onError: (error: string) => void
  initialData?: Partial<HeartDiseaseInput>
}

export function ManualForm({ onSubmit, onError, initialData }: ManualFormProps) {
  const [formData, setFormData] = useState<HeartDiseaseInput>({
    age: initialData?.age || 50,
    gender: initialData?.gender || 'Male',
    cholesterol: initialData?.cholesterol || 200,
    blood_pressure: initialData?.blood_pressure || 120,
    heart_rate: initialData?.heart_rate || 72,
    smoking: initialData?.smoking || 'Never',
    alcohol_intake: initialData?.alcohol_intake || 'None',
    exercise_hours: initialData?.exercise_hours || 3,
    family_history: initialData?.family_history || false,
    diabetes: initialData?.diabetes || false,
    obesity: initialData?.obesity || false,
    stress_level: initialData?.stress_level || 5,
    blood_sugar: initialData?.blood_sugar || 100,
    exercise_induced_angina: initialData?.exercise_induced_angina || false,
    chest_pain_type: initialData?.chest_pain_type || 'Asymptomatic',
  })

  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleInputChange = (field: keyof HeartDiseaseInput, value: any) => {
    setFormData((prev: HeartDiseaseInput) => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      // Basic validation
      if (formData.age < 18 || formData.age > 120) {
        throw new Error('Age must be between 18 and 120')
      }
      if (formData.cholesterol < 100 || formData.cholesterol > 600) {
        throw new Error('Cholesterol must be between 100 and 600 mg/dL')
      }
      if (formData.blood_pressure < 60 || formData.blood_pressure > 250) {
        throw new Error('Blood pressure must be between 60 and 250 mmHg')
      }
      if (formData.heart_rate < 40 || formData.heart_rate > 200) {
        throw new Error('Heart rate must be between 40 and 200 bpm')
      }
      if (formData.stress_level < 1 || formData.stress_level > 10) {
        throw new Error('Stress level must be between 1 and 10')
      }
      if (formData.blood_sugar < 70 || formData.blood_sugar > 300) {
        throw new Error('Blood sugar must be between 70 and 300 mg/dL')
      }
      if (formData.exercise_hours < 0 || formData.exercise_hours > 24) {
        throw new Error('Exercise hours must be between 0 and 24 per week')
      }

      onSubmit(formData)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Validation failed'
      onError(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ClipboardList className="h-5 w-5 text-blue-600" />
          Health Assessment Form
        </CardTitle>
        <CardDescription>
          Complete this comprehensive health questionnaire for personalized cardiovascular risk evaluation.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <User className="h-4 w-4" />
              Basic Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="age">Age (years)</Label>
                <Input
                  id="age"
                  type="number"
                  min="18"
                  max="120"
                  value={formData.age}
                  onChange={(e) => handleInputChange('age', parseInt(e.target.value) || 0)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="gender">Gender</Label>
                <Select value={formData.gender} onValueChange={(value) => handleInputChange('gender', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Male">Male</SelectItem>
                    <SelectItem value="Female">Female</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Health Metrics */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Health Metrics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="cholesterol">Cholesterol (mg/dL)</Label>
                <Input
                  id="cholesterol"
                  type="number"
                  min="100"
                  max="600"
                  value={formData.cholesterol}
                  onChange={(e) => handleInputChange('cholesterol', parseInt(e.target.value) || 0)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="blood_pressure">Blood Pressure (mmHg)</Label>
                <Input
                  id="blood_pressure"
                  type="number"
                  min="60"
                  max="250"
                  value={formData.blood_pressure}
                  onChange={(e) => handleInputChange('blood_pressure', parseInt(e.target.value) || 0)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="heart_rate">Heart Rate (bpm)</Label>
                <Input
                  id="heart_rate"
                  type="number"
                  min="40"
                  max="200"
                  value={formData.heart_rate}
                  onChange={(e) => handleInputChange('heart_rate', parseInt(e.target.value) || 0)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="blood_sugar">Blood Sugar (mg/dL)</Label>
                <Input
                  id="blood_sugar"
                  type="number"
                  min="70"
                  max="300"
                  value={formData.blood_sugar}
                  onChange={(e) => handleInputChange('blood_sugar', parseInt(e.target.value) || 0)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="stress_level">Stress Level (1-10)</Label>
                <Input
                  id="stress_level"
                  type="number"
                  min="1"
                  max="10"
                  value={formData.stress_level}
                  onChange={(e) => handleInputChange('stress_level', parseInt(e.target.value) || 1)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="exercise_hours">Exercise Hours/Week</Label>
                <Input
                  id="exercise_hours"
                  type="number"
                  min="0"
                  max="24"
                  value={formData.exercise_hours}
                  onChange={(e) => handleInputChange('exercise_hours', parseInt(e.target.value) || 0)}
                  required
                />
              </div>
            </div>
          </div>

          {/* Lifestyle Factors */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Heart className="h-4 w-4" />
              Lifestyle Factors
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="smoking">Smoking Status</Label>
                <Select value={formData.smoking} onValueChange={(value) => handleInputChange('smoking', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Never">Never</SelectItem>
                    <SelectItem value="Former">Former</SelectItem>
                    <SelectItem value="Current">Current</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="alcohol_intake">Alcohol Intake</Label>
                <Select value={formData.alcohol_intake} onValueChange={(value) => handleInputChange('alcohol_intake', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="None">None</SelectItem>
                    <SelectItem value="Moderate">Moderate</SelectItem>
                    <SelectItem value="Heavy">Heavy</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="chest_pain_type">Chest Pain Type</Label>
                <Select value={formData.chest_pain_type} onValueChange={(value) => handleInputChange('chest_pain_type', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Typical Angina">Typical Angina</SelectItem>
                    <SelectItem value="Atypical Angina">Atypical Angina</SelectItem>
                    <SelectItem value="Non-anginal Pain">Non-anginal Pain</SelectItem>
                    <SelectItem value="Asymptomatic">Asymptomatic</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Health Conditions */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Health Conditions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="family_history"
                  checked={formData.family_history}
                  onCheckedChange={(checked) => handleInputChange('family_history', checked)}
                />
                <Label htmlFor="family_history">Family History of Heart Disease</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="diabetes"
                  checked={formData.diabetes}
                  onCheckedChange={(checked) => handleInputChange('diabetes', checked)}
                />
                <Label htmlFor="diabetes">Diabetes</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="obesity"
                  checked={formData.obesity}
                  onCheckedChange={(checked) => handleInputChange('obesity', checked)}
                />
                <Label htmlFor="obesity">Obesity</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="exercise_induced_angina"
                  checked={formData.exercise_induced_angina}
                  onCheckedChange={(checked) => handleInputChange('exercise_induced_angina', checked)}
                />
                <Label htmlFor="exercise_induced_angina">Exercise Induced Angina</Label>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-4">
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? 'Processing...' : 'Predict Heart Disease Risk'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
