// Implementing Search Functionality

$(function() {
    var form = $('#search');
        form.find('button').click(function() {
        form.submit();
    });
});

// load search bar with search query
$(function() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const search_query = urlParams.get('q')
    if(search_query!=""){
      document.getElementById("q").value = search_query;
    }
});

// Extracting Category information
var cat_info = {}

var extract_cat_info = $('#catdesc').text().trim().split('\n')

extract_cat_info.forEach((element) => {
    if(element.trim().length > 10){
        keys = element.trim().split('--')
        cat_info[keys[0].trim()] = keys[1].trim()
    }
});

// Populating Tool Tip for Categories
$(".tooltip_info").each((idx, element) => {
    var id = element.id;
    element.attributes.title.value = cat_info[id];
});

// Implementing Curated Category Information above the tiles
let category_information_box = (selected_categories) => {
    $('#category-description').text('')
    var count = 0
    selected_categories.forEach(category => {
        if(!category.includes('any')){
            let temp = []
            if($('#category-description').text() != ''){
                temp.push($('#category-description').text());
            }
            temp.push(category + " - " + cat_info[category])
            let text_append =  temp.join(', ')
            $('#category-description').text(text_append);
        } else {
            count += 1
        }
    if(count < 3){
        $('#category-info').removeClass('d-none')
    } else {
        $('#category-info').addClass('d-none')
    }
    });
}


// Populating Curated Categories Tiles
var global_tiles = $('[curated_category]').parent();

let remove_tile = () => {
    var all_checked = $('input[type=radio]:checked');
    var count = 0
    all_checked.each((idx, element) => {
       if(element.value.includes('any')){
        count += 1
       }
    });
    if(count != 3){
        global_tiles.each((idx, element) =>{
            var cats = element.children[0].attributes.curated_category.value.split(',')
            element.children[0].children[0].children[0].children[0].innerText = cats.join(', ');
        });
    }
}

$(document).ready(function() {
    remove_tile()
});

Set.prototype.subSet = function(otherSet)
{
    for(var elem of this)
    {
        if(!otherSet.has(elem))
            return false;
    }
    return true;
}

$('input[type=radio]').change(function() {
    var get_attribs = [];
    var all_checked = $('input[type=radio]:checked')

    all_checked.each((idx, element) => {
        get_attribs.push(element.value)
    });

    var count_any = 0;

    get_attribs.forEach((element, idx) => {
        if(element.includes('any')){
            count_any += 1;
        }
    });

    if(count_any<3){
        global_tiles.each((idx, element) =>{
            var display = 'block';
            var current_cat = new Set(element.children[0].attributes.curated_category.value.split(','));
            var cc_head_legend = []
            get_attribs.forEach((element, idx) => {
                if(!element.includes('any')) {
                    if(!current_cat.has(element)){
                        display = 'none';
                    }
                    cc_head_legend.push(element)
                }
            });
            element.style.display = display;
            var temp_text = cc_head_legend.join(', ');
            element.children[0].children[0].children[0].children[0].innerText = temp_text;
        });
    } else {
        global_tiles.each((idx, element) =>{
            element.style.display = 'block';
            var cats = element.children[0].attributes.curated_category.value.split(',')
            element.children[0].children[0].children[0].children[0].innerText = cats.join(', ');
        });
    }
    category_information_box(get_attribs);
});

$(function(){
  $("input[type=radio]").trigger('change');
});
