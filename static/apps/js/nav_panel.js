$(function() {
    var form = $('#search');
        form.find('button').click(function() {
        form.submit();
    });
});

var global_tiles = $('[curated_category]').parent();

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
            get_attribs.forEach((element, idx) => {
                if(!element.includes('any')) {
                    if(!current_cat.has(element)){
                        display = 'none';
                    }
                }
            });
            element.style.display = display;
        });
    } else {
        global_tiles.each((idx, element) =>{
            element.style.display = 'block';
        });
    }
});

