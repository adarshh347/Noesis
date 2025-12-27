import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Weltanschauung - Philosophy Beyond Text',
  description: 'Transforming abstract thoughts into visible, interactive insights',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

