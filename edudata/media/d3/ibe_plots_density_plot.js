density_plot = function(data, parent, main) {
    /* parametry wykresu */
    var xMax = d3.max(data), 
        xMin = d3.min(data);
    /* parametry skali */
    var x = d3.scale.linear()
                    .domain([0, data.length])
                    .range([0 + margin.left, width - margin.right]), 
        y = d3.scale.linear()
                    .domain([0, d3.max(data)])
                    .range([height - margin.top - 5,        // -5 by odsunąć linię wykresu od osi X
                            margin.bottom + margin.top]);
    // osie
    var xAxis = d3.svg.axis().scale(x).orient('bottom'), 
        yAxis = d3.svg.axis().scale(y).orient('left');
    /* konstrukcja okna svg */
    var svg = d3.select(parent)
                .append('svg')
                .attr('width', width)
                .attr('height', height)
                .attr('class', 'svg_in_box');
    /* funkcja: narysuj powierzchnię */
    var line = d3.svg.line()
                 .y(function(d) { return y(d); })
                 .x(function(d, i) { return x(i); })
                 .interpolate('cardinal'); // wygładzanie
    /* dołącz osie */
    var svg = svg.append("g")
                 .attr("class", "x axis")
                 .attr("transform", "translate(0," + (height-margin.bottom) + ")")
                 .call(xAxis);
    var svg = d3.selectAll('svg').append('g')
                 .attr("class", "y axis")
                 .attr("transform", "translate("+margin.left+","+-10+")")
                 .call(yAxis);  
    /* dołącz element path */
    var svg = svg.append('path')
                 .datum(data)
                 .attr('class', 'line')
                 .attr('d', line);
    // tytuł:
    var svg = d3.selectAll('svg');
    var svg = svg.append('text').text(main)
                                .attr('x', width * 0.5)
                                .attr('y', margin.top * 0.5)
                                .attr('class', 'text_main');
    return svg;
};
