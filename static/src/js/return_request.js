
$(function(){
    var dtToday = new Date();

    var month = dtToday.getMonth() + 1;
    var day = dtToday.getDate();
    var year = dtToday.getFullYear();

    if(month < 10)
        month = '0' + month.toString();
    if(day < 10)
        day = '0' + day.toString();

    var maxDate = year + '-' + month + '-' + day;
    $('#txtDateFuture').attr('max', maxDate);
});





$(function () {

    // Start counting from the third row
    var counter = 1;

    $("#insertRow").on("click", function (event) {
        event.preventDefault();

        var newRow = $("<tr>");
        var cols = '';
        // Table columns
//        cols += '<th scrope="row">' + counter + '</th>';

        cols += '<td><input class="form-control s_website_form_input" id="txtDateFuture" type="date" name="date"></td>';
        cols += '<td> <select class="form-control s_website_form_input" id="product_type" name="product_type" required="1"> <option value="">Select an option</option><option value="newspaper">NewsPaper</option><option value="magazine">Magazine</option></select></td>';
        cols += '<td> <select class="form-control s_website_form_input" id="return_type" name="return_type" required="1"> <option value="">Select an option</option><option value="full_paper">Full Paper</option><option value="master_head">Master Head</option></select></td>';
        cols += '<td><input class="container" type="text" name="no_of_copies" pattern="[0-9]+" title="Please enter only numbers." required></td>';
        cols += '<td><input class="container" type="text" name="weight" pattern="[0-9]+" title="Please enter only numbers." required></td>';
        cols += '<td></td>';
        cols += '<td><button type="submit" class="btn btn-primary">Send</button></td>';
        cols += '<td><button class="btn btn-danger_new rounded-0" id ="deleteRow"><i class="fa fa-trash"></i></button</td>';

        // Insert the columns inside a row
        newRow.append(cols);

        // Insert the row inside a table
        $("table").append(newRow);

        // Increase counter after each row insertion
        counter++;
    });

    // Remove row when delete btn is clicked
    $("table").on("click", "#deleteRow", function (event) {
        $(this).closest("tr").remove();
        counter -= 1
    });
});








