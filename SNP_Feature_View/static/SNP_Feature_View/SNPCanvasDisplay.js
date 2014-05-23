var displaySNPSequence = function(canvas, leftFlank, rightFlank, snp, parentNum, xPos, yPos) {
    var context = canvas.getContext("2d");
    var flankFont = "bold 15px Arial";
    var flankColor = "#333";
    var snpFont = "bold 38px Arial";
    var snpColor = "blue";
    var parentFont = "bold 16px Arial";
    var parentColor = "#900000";
    var currentXPos = xPos;
      
    context.font= flankFont;
    context.fillStyle = flankColor; 
    var threeDotWidth = context.measureText("...").width;
    context.fillText("...", xPos, yPos); 
    currentXPos += threeDotWidth;

    var lFlankWidth = context.measureText(leftFlank).width;
    context.fillText(leftFlank, currentXPos, yPos);
    currentXPos += lFlankWidth;

    context.font = snpFont; 
    context.fillStyle = snpColor;
    var bigCharWidth = context.measureText(snp).width;
    context.fillText(snp, currentXPos, yPos);
    currentXPos += bigCharWidth; 
                
    context.font = flankFont; 
    context.fillStyle = flankColor; 
    var rFlankWidth = context.measureText(rightFlank).width;
    context.fillText(rightFlank, currentXPos, yPos); 
    currentXPos += rFlankWidth;
                
    context.fillText("...", currentXPos, yPos); 
    currentXPos += threeDotWidth;

    context.font = parentFont; 
    context.fillStyle = parentColor;
    context.fillText("     " + parentNum, currentXPos, yPos);         
};
