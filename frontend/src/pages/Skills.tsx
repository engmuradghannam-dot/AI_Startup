import { useQuery, useQueryClient } from 'react-query'
import { useState } from 'react'
import SkillPanel from '../components/SkillPanel'
import { skillsApi } from '../services/api'

export default function Skills() {
  const queryClient = useQueryClient()
  const [selectedCategory, setSelectedCategory] = useState('all')

  const { data: skillsResponse, isLoading: skillsLoading } = useQuery(
    'skills',
    () => skillsApi.list().then((r: any) => r.data),
    { refetchInterval: 30000 }
  )

  const { data: categoriesResponse } = useQuery(
    'skillCategories',
    () => skillsApi.getCategories().then((r: any) => r.data)
  )

  // ✅ Ensure skills is always an Array
  const skills = Array.isArray(skillsResponse) ? skillsResponse : []

  // ✅ Ensure categories is always an Object
  const categories = (categoriesResponse && typeof categoriesResponse === 'object' && !Array.isArray(categoriesResponse))
    ? categoriesResponse
    : {}

  const categories_list = [
    { id: 'all', label: 'All Skills', count: skills.length },
    { id: 'fable5', label: 'Fable 5', count: categories.fable5?.total || 0 },
    { id: 'orchestration', label: 'Orchestration', count: categories.orchestration?.total || 0 },
    { id: 'scaling', label: 'Scaling', count: categories.scaling?.total || 0 },
    { id: 'optimization', label: 'Optimization', count: categories.optimization?.total || 0 },
    { id: 'security', label: 'Security', count: categories.security?.total || 0 },
    { id: 'monitoring', label: 'Monitoring', count: categories.monitoring?.total || 0 },
    { id: 'learning', label: 'Learning', count: categories.learning?.total || 0 },
    { id: 'deployment', label: 'Deployment', count: categories.deployment?.total || 0 },
    { id: 'multimodal', label: 'Multi-Modal', count: categories.multimodal?.total || 0 },
  ]

  const filteredSkills = selectedCategory === 'all'
    ? skills
    : skills.filter((s: any) => s.category === selectedCategory)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Skills</h1>
        <p className="text-gray-600 mt-1">Manage agent skills and capabilities</p>
      </div>

      {/* Categories */}
      <div className="flex flex-wrap gap-2">
        {categories_list.map((cat: any) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedCategory === cat.id
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {cat.label} ({cat.count})
          </button>
        ))}
      </div>

      {/* Skills Grid */}
      {skillsLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto" />
          <p className="text-gray-500 mt-4">Loading skills...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
    </div>
  )
}
