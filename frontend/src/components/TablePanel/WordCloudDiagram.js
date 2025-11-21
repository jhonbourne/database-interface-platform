import ReactEcharts from "echarts-for-react";
import "echarts-wordcloud";

function WordCloudDiagram({info}) {
    const success = info && info.success;
    if (success) {
        let wordData = info.data;

        const option = {
            backgroundColor: "#fff",
            tooltip: {
                pointFormat: "{series.name}: <b>{point.percentage:.1f}%</b>"
            },
            series: [
                {
                type: "wordCloud",
                gridSize: 1,
                // Text size range which the value in data will be mapped to.
                // Default to have minimum 12px and maximum 60px size.
                sizeRange: [8, 55],
                rotationRange: [0, 0],  // Angle of word rotation
                textStyle: {  // Color of presented words
                    color: function() {
                        return (
                        "rgb(" +
                        Math.round(Math.random() * 255) +
                        ", " +
                        Math.round(Math.random() * 255) +
                        ", " +
                        Math.round(Math.random() * 255) +
                        ")"
                        );
                    }
                },
                // Folllowing left/top/width/height/right/bottom are used for positioning the word cloud
                // Default to be put in the center and has 75% x 80% size.
                left: "center",
                top: "center",
                width: "100%",
                height: "100%",
                data: wordData
                }
            ]
        };
        return (
            <ReactEcharts
                // echarts={echarts}
                option={option}
                style={{ height: '600px', width: '100%' }}
            />
        )

    } else {
        // fallback when no data or failed
        const status = (info && info.status) || 'No data available.';
        return (
            <div style={{ padding: 16 }}>
                <h3>{status}</h3>
            </div>
        );
    }
}

export default WordCloudDiagram;