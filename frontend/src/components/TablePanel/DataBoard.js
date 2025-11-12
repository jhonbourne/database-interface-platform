import ReactECharts from 'echarts-for-react';

/**
 * DataBoard renders table-like data using echarts matrix coordinate system.
 * It fixes a per-row height so rows have consistent height and the overall
 * chart height grows with the number of rows, allowing the page length to
 * vary accordingly.
 *
 * Props:
 *  - info: { success: boolean, data: Array<Array>, columns: Array, status?: string }
 *  - rowHeight: optional number (px) per row, default 40
 */
const DataBoard = ({ info, rowHeight = 40 }) => {
    const success = info && info.success;
    if (success) {
        const row_len = (info.data && info.data.length) || 0;
        const col_len = (info.columns && info.columns.length) || 0;

        // assemble data for echarts matrix: [column, rowIndex, value]
        const data = [];
        for (let i = 1; i <= row_len; i++) {
            for (let j = 0; j < col_len; j++) {
                data.push([info.columns[j], i.toString(), String(info.data[i - 1][j])]);
            }
        }

        const option = {
            matrix: {
                y: {
                    data: Array(row_len).fill(null).map((_,i) => (i+1).toString()),
                    show: false
                },
                x: {
                    data: info.columns,
                    label: {
                        fontSize: 16,
                        color: '#000'
                    }
                },
                top: 24
            },
            // visualMap: {
            //     type: 'continuous',
            //     show: false,
                
            // },
            series: {
                renderItem: (params, api) => {
                    const x = api.value(0);
                    const y = api.value(1);
                    const rect = api.layout([x, y]).rect;
                    const margin = 2;
                    return {
                        type: 'rect',
                        shape: {
                            x: rect.x + margin,
                            y: rect.y + margin,
                            width: rect.width - margin * 2,
                            height: rect.height - margin * 2
                        },
                        style: api.style({
                            fill: '#fff',
                            stroke: '#ddd',
                            lineWidth: 0
                        })
                    };
                },
                type: 'custom',
                coordinateSystem: 'matrix',
                data: data,
                label: {
                    show: true,
                    formatter: (params) => String(params.value[2]),
                    textStyle: {
                        fontSize: 12,
                        align: 'center',
                        color: '#000'
                    }
                }
            }
            // ,dataZoom: [
            //     {
            //         type: 'slider',
            //         show: true,
            //         yAxisIndex: [0],
            //         width: 8,
            //         right: 10,
            //         startValue: 0,
            //         endValue: Math.min(row_len, 10)
            //     },
            //     {
            //         type: 'inside',
            //         yAxisIndex: [0],
            //         zoomOnMouseWheel: true,
            //         moveOnMouseMove: true
            //     }
            // ]
        };

        // Calculate chart height: give some padding for headers, margins and controls
        const computedHeight = row_len * rowHeight;
        return <ReactECharts 
                    option={option} 
                    style={{ 
                        height: `${computedHeight}px`
                     }} 
                />;
    } else {
        // fallback when no data or failed
        const status = (info && info.status) || 'No data available.';
        return (
            <div style={{ padding: 16 }}>
                <h3>{status}</h3>
            </div>
        );
    }    
};

export default DataBoard;