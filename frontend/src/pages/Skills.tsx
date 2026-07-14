import { useQuery, useQueryClient } from 'react-query'
import { useState } from 'react'
import SkillPanel from '../components/SkillPanel'
import { skillsApi } from '../services/api'

export default function Skills() {
  const queryClient = useQueryClient()
  const [selectedCategory, setSelectedCategory] = useState('all')

  const { data: skills, isLoading } = useQuery(
    'skills',
    () => skillsApi.list().then(r => r.data),
    { refetchInterval: 30000 }
  )

  const { data: categories } = useQuery(
    'skillCategories',
    () => skillsApi.getCategories().then(r => r.data)
  )

  // ✅ Ensure skills is always an Array
  const skillsArray = Array.isArray(skills) ? skills : []

  // ✅ Ensure categories is always an Object
  const categoriesObj = (categories && typeof categories === 'object' && !Array.isArray(categories))
    ? categories
    : {}

  const categories_list = [
    { id: 'all', label: 'All Skills', count: skillsArray.length },
    { id: 'fable5', label: 'Fable 5', count: categoriesObj.fable5?.total || 0 },
    { id: 'orchestration', label: 'Orchestration', count: categoriesObj.orchestration?.total || 0 },
    { id: 'scaling', label: 'Scaling', count: categoriesObj.scaling?.total || 0 },
    { id: 'optimization', label: 'Optimization', count: categoriesObj.optimization?.total || 0 },
    { id: 'security', label: 'Security', count: categoriesObj.security?.total || 0 },
    { id: 'monitoring', label: 'Monitoring', count: categoriesObj.monitoring?.total || 0 },
    { id: 'learning', label: 'Learning', count: categoriesObj.learning?.total || 0 },
    { id: 'deployment', label: 'Deployment', count: categoriesObj.deployment?.total || 0 },
    { id: 'multimodal', label: 'Multi-Modal', count: categoriesObj.multimodal?.total || 0 },
    { id: 'collaboration', label: 'Collaboration', count: categoriesObj.collaboration?.total || 0 },
  ]

  const filteredSkills = selectedCategory === 'all'
    ? skillsArray
    : skillsArray.filter((s: any) => s.category === selectedCategory)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Skills</h1>
        <p className="text-gray-600 mt-1">Manage and configure agent skills</p>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {categories_list.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedCategory === cat.id
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
            }`}
          >
            {cat.label} ({cat.count})
          </button>
        ))}
      </div>

      {/* Skills Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSkills.map((skill: any) => (
            <SkillPanel
              key={skill.id || skill._id || Math.random()}
              skill={skill}
              onUpdate={() => queryClient.invalidateQueries('skills')}
            />
          ))}
          {filteredSkills.length === 0 && (
            <div className="col-span-full text-center py-12 text-gray-500">
              No skills found
            </div>
          )}
        </div>
      )}

      {/* Skills Summary */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mt-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Skills Overview</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
          <div className="p-4 bg-purple-50 rounded-lg">
            <p className="text-2xl font-bold text-purple-700">10</p>
            <p className="text-sm text-purple-600">Fable 5 Skills</p>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-2xl font-bold text-blue-700">15</p>
            <p className="text-sm text-blue-600">Advanced Skills</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-700">
              {skillsArray.filter((s: any) => s.enabled).length}
            </p>
            <p className="text-sm text-green-600">Active</p>
          </div>
          <div className="p-4 bg-yellow-50 rounded-lg">
            <p className="text-2xl font-bold text-yellow-700">
              {skillsArray.filter((s: any) => !s.enabled).length}
            </p>
            <p className="text-sm text-yellow-600">Inactive</p>
          </div>
          <div className="p-4 bg-red-50 rounded-lg">
            <p className="text-2xl font-bold text-red-700">
              {skillsArray.reduce((acc: number, s: any) => acc + (s.metrics?.total_executions || 0), 0)}
            </p>
            <p className="text-sm text-red-600">Total Executions</p>
          </div>
        </div>
      </div>
    </div>
  )
}
