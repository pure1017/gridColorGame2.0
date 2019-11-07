var enable = 0;
function show_confirm()
{
  var r=confirm("Color Sensitive Game!\n In this small grid game, you need to click on the square that has different " +
    "color. There is only a slight difference.\n Are you ready? Let's go!");
  if (r==true)
  {
    enable = 1;
    countdown();
  }
  // else
  // {
  //   alert("You pressed Cancel!");
  // }
}

var div = d3.select("body")
  .append("div")
  .attr("id", "mouseover")
  .attr("class", "decisionMenu")
  .style("opacity", 1);
div.append('button')
  .attr("id", "buttonStart")
  .attr("type", "button")
  .text("START")
  .on("click", show_confirm);
