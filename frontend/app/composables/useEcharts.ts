import { use, type EChartsOption } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import {
  ScatterChart,
  BarChart,
  LineChart,
  HeatmapChart,
  EffectScatterChart,
} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent,
  VisualMapComponent,
  MarkLineComponent,
  MarkPointComponent,
} from 'echarts/components'

use([
  CanvasRenderer,
  ScatterChart, BarChart, LineChart, HeatmapChart, EffectScatterChart,
  TitleComponent, TooltipComponent, LegendComponent, GridComponent,
  DataZoomComponent, ToolboxComponent, VisualMapComponent,
  MarkLineComponent, MarkPointComponent,
])

export { type EChartsOption }

export const CHART_COLORS = {
  primary: '#003CA6',
  primaryLight: '#1a5fd4',
  yellow: '#FFD600',
  green: '#00E5A0',
  red: '#FF3366',
  blue: '#60a5fa',
  purple: '#a78bfa',
  text: '#E8E8E8',
  textMuted: 'rgba(255,255,255,0.5)',
  grid: 'rgba(255,255,255,0.06)',
  bg: 'transparent',
  tooltipBg: 'rgba(6,6,20,0.95)',
  tooltipBorder: 'rgba(0,60,166,0.4)',
}

export const baseTooltip = {
  backgroundColor: CHART_COLORS.tooltipBg,
  borderColor: CHART_COLORS.tooltipBorder,
  borderWidth: 1,
  textStyle: { color: CHART_COLORS.text, fontSize: 12, fontFamily: 'Inter, sans-serif' },
  extraCssText: 'backdrop-filter:blur(12px);border-radius:8px;box-shadow:0 8px 32px rgba(0,0,0,0.4);',
}

export const baseChartOption: Partial<EChartsOption> = {
  backgroundColor: CHART_COLORS.bg,
  textStyle: {
    color: CHART_COLORS.text,
    fontFamily: 'Inter, sans-serif',
  },
  grid: {
    containLabel: true,
    left: 16,
    right: 16,
    top: 48,
    bottom: 16,
  },
  animationDuration: 800,
  animationEasing: 'cubicInOut',
}
