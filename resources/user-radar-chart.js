function renderRadarChart(container, data) {
    var W = container.clientWidth || 400;
    var H = container.clientHeight || 280;
    var cx = W / 2, cy = H / 2;
    var radius = Math.min(cx, cy) - 30;
    var levels = 5;

    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', W);
    svg.setAttribute('height', H);
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.style.display = 'block';

    var labels = data && data.length ? data.map(function (d) { return d.label; }) : [];
    var values = data && data.length ? data.map(function (d) { return d.value; }) : [];
    var maxVal = 1;
    if (values.length) {
        for (var i = 0; i < values.length; i++) {
            if (values[i] > maxVal) maxVal = values[i];
        }
    }
    var n = labels.length || 6;
    var angleStep = (Math.PI * 2) / n;

    // Grid - concentric polygons
    for (var level = 1; level <= levels; level++) {
        var r = (radius / levels) * level;
        var pts = '';
        for (var i = 0; i < n; i++) {
            var a = -Math.PI / 2 + i * angleStep;
            var x = cx + r * Math.cos(a);
            var y = cy + r * Math.sin(a);
            pts += (i ? ',' : '') + x.toFixed(1) + ',' + y.toFixed(1);
        }
        var poly = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        poly.setAttribute('points', pts);
        poly.setAttribute('fill', 'none');
        poly.setAttribute('stroke', '#333');
        poly.setAttribute('stroke-width', '0.5');
        svg.appendChild(poly);
    }

    // Axes
    for (var i = 0; i < n; i++) {
        var a = -Math.PI / 2 + i * angleStep;
        var x = cx + radius * Math.cos(a);
        var y = cy + radius * Math.sin(a);
        var line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', cx);
        line.setAttribute('y1', cy);
        line.setAttribute('x2', x.toFixed(1));
        line.setAttribute('y2', y.toFixed(1));
        line.setAttribute('stroke', '#333');
        line.setAttribute('stroke-width', '0.5');
        svg.appendChild(line);

        if (labels[i]) {
            var txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            var labelR = radius + 14;
            var lx = cx + labelR * Math.cos(a);
            var ly = cy + labelR * Math.sin(a);
            txt.setAttribute('x', lx.toFixed(1));
            txt.setAttribute('y', ly.toFixed(1));
            txt.setAttribute('text-anchor', 'middle');
            txt.setAttribute('dominant-baseline', 'middle');
            txt.setAttribute('fill', '#888');
            txt.setAttribute('font-family', 'JetBrains Mono, monospace');
            txt.setAttribute('font-size', '10');
            txt.textContent = labels[i];
            svg.appendChild(txt);
        }
    }

    // Data polygon
    if (values.length) {
        var pts = '';
        for (var i = 0; i < n; i++) {
            var v = i < values.length ? values[i] : 0;
            var r = (v / maxVal) * radius;
            var a = -Math.PI / 2 + i * angleStep;
            var x = cx + r * Math.cos(a);
            var y = cy + r * Math.sin(a);
            pts += (i ? ',' : '') + x.toFixed(1) + ',' + y.toFixed(1);
        }
        var dataPoly = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        dataPoly.setAttribute('points', pts);
        dataPoly.setAttribute('fill', 'rgba(255, 107, 0, 0.2)');
        dataPoly.setAttribute('stroke', '#FF6B00');
        dataPoly.setAttribute('stroke-width', '1.5');
        svg.appendChild(dataPoly);

        // Data points
        for (var i = 0; i < n; i++) {
            var v = i < values.length ? values[i] : 0;
            var r = (v / maxVal) * radius;
            var a = -Math.PI / 2 + i * angleStep;
            var x = cx + r * Math.cos(a);
            var y = cy + r * Math.sin(a);
            var dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            dot.setAttribute('cx', x.toFixed(1));
            dot.setAttribute('cy', y.toFixed(1));
            dot.setAttribute('r', '3');
            dot.setAttribute('fill', '#FF6B00');
            svg.appendChild(dot);
        }
    } else {
        // Empty state
        var txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        txt.setAttribute('x', cx);
        txt.setAttribute('y', cy);
        txt.setAttribute('text-anchor', 'middle');
        txt.setAttribute('dominant-baseline', 'middle');
        txt.setAttribute('fill', '#666');
        txt.setAttribute('font-family', 'JetBrains Mono, monospace');
        txt.setAttribute('font-size', '12');
        txt.textContent = 'No topic data';
        svg.appendChild(txt);
    }

    container.innerHTML = '';
    container.appendChild(svg);
}
