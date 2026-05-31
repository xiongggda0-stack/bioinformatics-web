"use client";

import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";

interface BenchmarkSeries {
  name: string;
  unit: string;
  y_axis: "time" | "memory";
  data: number[];
}

interface BenchmarkData {
  x_axis?: string[];
  series?: BenchmarkSeries[];
  environment?: string;
}

interface BenchmarkChartProps {
  performanceJson: BenchmarkData | Record<string, unknown>;
}

function isBenchmarkSeries(value: unknown): value is BenchmarkSeries {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const item = value as Record<string, unknown>;
  return (
    typeof item.name === "string" &&
    typeof item.unit === "string" &&
    (item.y_axis === "time" || item.y_axis === "memory") &&
    Array.isArray(item.data) &&
    item.data.every((point) => typeof point === "number")
  );
}

function normalizeBenchmarkData(
  performanceJson: BenchmarkChartProps["performanceJson"]
): Required<BenchmarkData> {
  const xAxis = Array.isArray(performanceJson.x_axis)
    ? performanceJson.x_axis.filter((item): item is string => typeof item === "string")
    : [];
  const series = Array.isArray(performanceJson.series)
    ? performanceJson.series.filter(isBenchmarkSeries)
    : [];
  const environment =
    typeof performanceJson.environment === "string"
      ? performanceJson.environment
      : "Benchmark environment not specified";

  return { x_axis: xAxis, series, environment };
}

export default function BenchmarkChart({
  performanceJson
}: BenchmarkChartProps): JSX.Element {
  const benchmark = normalizeBenchmarkData(performanceJson);
  const timeSeries = benchmark.series.find((item) => item.y_axis === "time");
  const memorySeries = benchmark.series.find((item) => item.y_axis === "memory");
  const hasData = benchmark.x_axis.length > 0 && benchmark.series.length > 0;

  const option: EChartsOption = {
    color: ["#0f766e", "#f9735b"],
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
      backgroundColor: "rgba(15, 23, 42, 0.94)",
      borderColor: "rgba(103, 232, 249, 0.35)",
      textStyle: { color: "#e0f2fe" }
    },
    legend: {
      top: 8,
      right: 8,
      textStyle: { color: "#475569", fontWeight: 600 }
    },
    grid: {
      left: 54,
      right: 58,
      top: 58,
      bottom: 44
    },
    xAxis: {
      type: "category",
      data: benchmark.x_axis,
      axisLine: { lineStyle: { color: "#cbd5e1" } },
      axisTick: { show: false },
      axisLabel: { color: "#64748b", fontWeight: 600 }
    },
    yAxis: [
      {
        type: "value",
        name: timeSeries ? timeSeries.unit : "时间",
        position: "left",
        axisLabel: { color: "#0f766e" },
        splitLine: { lineStyle: { color: "#e2e8f0", type: "dashed" } },
        nameTextStyle: { color: "#0f766e", fontWeight: 700 }
      },
      {
        type: "value",
        name: memorySeries ? memorySeries.unit : "内存",
        position: "right",
        axisLabel: { color: "#f9735b" },
        splitLine: { show: false },
        nameTextStyle: { color: "#f9735b", fontWeight: 700 }
      }
    ],
    series: benchmark.series.map((item) => ({
      name: `${item.name} (${item.unit})`,
      type: item.y_axis === "time" ? "bar" : "line",
      smooth: item.y_axis === "memory",
      yAxisIndex: item.y_axis === "time" ? 0 : 1,
      data: item.data,
      barWidth: item.y_axis === "time" ? 34 : undefined,
      symbolSize: item.y_axis === "memory" ? 9 : undefined,
      lineStyle: item.y_axis === "memory" ? { width: 3 } : undefined,
      itemStyle:
        item.y_axis === "time"
          ? {
              borderRadius: [6, 6, 0, 0],
              shadowBlur: 12,
              shadowColor: "rgba(15, 118, 110, 0.18)"
            }
          : undefined
    }))
  };

  return (
    <section className="mb-8 rounded border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 pb-4">
        <div>
          <h2 className="text-lg font-semibold text-ink">性能基准测试</h2>
          <p className="mt-1 text-sm text-slate-500">{benchmark.environment}</p>
        </div>
        <span className="rounded bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-700 ring-1 ring-cyan-200">
          Benchmark
        </span>
      </div>

      {hasData ? (
        <ReactECharts option={option} style={{ height: 360, width: "100%" }} />
      ) : (
        <div className="flex min-h-64 items-center justify-center rounded border border-dashed border-slate-300 bg-slate-50 text-sm font-semibold text-slate-500">
          暂无可视化基准测试数据
        </div>
      )}
    </section>
  );
}
