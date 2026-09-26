import React from 'react'
import { getRiskBadge } from '../utils/helpers.js'

export default function RiskBadge({ level }) {
  return <span className={getRiskBadge(level)}>{level}</span>
}
