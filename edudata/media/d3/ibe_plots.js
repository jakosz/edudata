// ----------------------------------------------------------------------------- plots:

/* funkcja density plot
    Obecności jakich zmiennych w przestrzeni nazw oczekuje funkcja density_plot?
        * margin = { top: a, bottom: b, left: c, right: d }
        * width, height
*/
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

var hist = function(values) { 

    var xMar = d3.max(values) * 0.05, 
        xMin = d3.min(values) - xMar, 
        xMax = d3.max(values) + xMar;

    // A formatter for counts.
    var formatCount = d3.format(",.0f");

    var margin = {top: 100, right: 30, bottom: 30, left: 30},
        width = 1111 - margin.left - margin.right,
        height = 250 - margin.top - margin.bottom;

    var x = d3.scale.linear()
        .domain([xMin, xMax])
        .range([0, width]);

    // Generate a histogram using twenty uniformly-spaced bins.
    var data = d3.layout.histogram()
        .bins(x.ticks(20))
        (values);

    var y = d3.scale.linear()
        .domain([0, d3.max(data, function(d) { return d.y; })])
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .ticks(9)
        .orient("bottom");

    // TODO: ogarnąć szczegóły powyższych zmiennych

    var bar_width = width / data.length, 
        bar_width = Math.round(bar_width * 0.9);

    var svg = d3.select("td").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var bar = svg.selectAll(".bar")
        .data(data)
      .enter().append("g")
        .attr("class", "bar")
        .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

    bar.append("rect")
        .attr("x", 1)
        .attr("width", bar_width)
        .attr("height", function(d) { return height - 3 - y(d.y); });

    console.log(bar_width)

    //  funckcja pomocznia a la R-owa ifelse do generowania atrybutów:

    var ifelse = 
        function(test, if_true, if_false) {
            if (test) {
                return if_true;
            } else {
                return if_false;
            }
        }

    bar.append("text")
        .attr("dy", function(d) { return ifelse(d.y > 40, '1em', '-1em');})
        .attr("y", 6)
        .attr("x", bar_width * 0.5)
        .attr("text-anchor", "middle")
        .attr('fill', function(d) { return ifelse(d.y > 40, 'white', 'steelblue'); })
        .text(function(d) { return formatCount(d.y); });

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);
        
    return svg;
}

// ----------------------------------------------------------------------------- utils:

//  a la R-owa ifelse:
var ifelse = 
    function(test, if_true, if_false) {
        if (test) {
            return if_true;
        } else {
            return if_false;
        }
    }
    
// 
