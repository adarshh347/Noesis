'use client'

import { ThemeDistribution } from '@/types'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface ThemeChartProps {
  data: ThemeDistribution[]
}

export default function ThemeChart({ data }: ThemeChartProps) {
  const colors = ['#e94560', '#533483', '#0f3460', '#16213e', '#1a1a2e']

  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#533483" />
          <XAxis 
            dataKey="theme" 
            stroke="#9ca3af"
            angle={-45}
            textAnchor="end"
            height={100}
          />
          <YAxis stroke="#9ca3af" />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1a1a2e', 
              border: '1px solid #533483',
              borderRadius: '8px'
            }}
          />
          <Bar dataKey="weight" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

