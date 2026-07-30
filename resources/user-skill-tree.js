function renderSkillTree(data) {
    var container = document.getElementById('skill-tree-svg');
    if (!container || !data.nodes || !data.nodes.length) return;

    var width = container.parentElement.clientWidth || 600;
    var height = 380;

    var svg = d3.select('#skill-tree-svg')
        .attr('viewBox', '0 0 ' + width + ' ' + height)
        .attr('preserveAspectRatio', 'xMidYMid meet');

    svg.selectAll('*').remove();

    var nodes = data.nodes.map(function (n) {
        return Object.assign({}, n, { solved: n.solved || 0 });
    });
    var links = data.links || [];

    var maxSolved = 1;
    nodes.forEach(function (n) { if (n.solved > maxSolved) maxSolved = n.solved; });

    var colorScale = d3.scaleLinear()
        .domain([0, maxSolved * 0.33, maxSolved * 0.66, maxSolved])
        .range(['#E0E0E0', '#FFB366', '#FF8C00', '#FF6B00']);

    var radiusScale = d3.scaleLinear()
        .domain([0, maxSolved])
        .range([12, 32]);

    var simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(function (d) { return d.id; }).distance(80))
        .force('charge', d3.forceManyBody().strength(-200))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(function (d) { return radiusScale(d.solved) + 4; }));

    var link = svg.append('g')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('stroke', '#D0D0D0')
        .attr('stroke-width', 1.5);

    var node = svg.append('g')
        .selectAll('g')
        .data(nodes)
        .join('g')
        .call(d3.drag()
            .on('start', function (event, d) { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
            .on('drag', function (event, d) { d.fx = event.x; d.fy = event.y; })
            .on('end', function (event, d) { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }));

    node.append('circle')
        .attr('r', function (d) { return radiusScale(d.solved); })
        .attr('fill', function (d) { return colorScale(d.solved); })
        .attr('stroke', '#1A1A1A')
        .attr('stroke-width', 1);

    node.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', function (d) { return radiusScale(d.solved) + 14; })
        .attr('font-size', '0.65rem')
        .attr('font-family', 'JetBrains Mono, monospace')
        .attr('fill', '#1A1A1A')
        .text(function (d) { return d.label.length > 14 ? d.label.slice(0, 12) + '..' : d.label; });

    node.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', function (d) { return radiusScale(d.solved) + 26; })
        .attr('font-size', '0.6rem')
        .attr('font-family', 'JetBrains Mono, monospace')
        .attr('fill', '#888')
        .text(function (d) { return d.solved + ' solved'; });

    simulation.on('tick', function () {
        link.attr('x1', function (d) { return d.source.x; })
            .attr('y1', function (d) { return d.source.y; })
            .attr('x2', function (d) { return d.target.x; })
            .attr('y2', function (d) { return d.target.y; });

        node.attr('transform', function (d) { return 'translate(' + d.x + ',' + d.y + ')'; });
    });
}