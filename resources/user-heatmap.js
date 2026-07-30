function renderHeatmap(canvas, data) {
    var ctx = canvas.getContext('2d');
    var W = canvas.width, H = canvas.height;
    var cellSize = 10, gap = 2;
    var cols = 53, rows = 7;
    var startX = 20, startY = 20;
    var maxVal = 1;
    for (var k in data) { if (data[k] > maxVal) maxVal = data[k]; }

    ctx.fillStyle = '#FAFAFA';
    ctx.fillRect(0, 0, W, H);

    var dates = Object.keys(data).sort();
    var dayStrings = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
    for (var r = 0; r < rows; r++) {
        ctx.fillStyle = '#1A1A1A';
        ctx.font = '8px JetBrains Mono, monospace';
        ctx.textAlign = 'right';
        ctx.fillText(dayStrings[r], startX - 4, startY + r * (cellSize + gap) + 8);
    }

    var firstDate = new Date(dates[0] || Date.now());
    var startDay = firstDate.getDay();
    var col = 0, row = startDay;
    dates.forEach(function (iso) {
        var val = data[iso] || 0;
        var intensity = val / maxVal;
        var color;
        if (val === 0) color = '#E0E0E0';
        else if (intensity < 0.33) color = '#FFB366';
        else if (intensity < 0.66) color = '#FF8C00';
        else color = '#FF6B00';

        ctx.fillStyle = color;
        var x = startX + col * (cellSize + gap);
        var y = startY + row * (cellSize + gap);
        ctx.fillRect(x, y, cellSize, cellSize);
        ctx.strokeStyle = '#D0D0D0';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(x, y, cellSize, cellSize);

        row++;
        if (row >= 7) { row = 0; col++; }
    });

    canvas.title = 'Submission Activity Heatmap';
}
