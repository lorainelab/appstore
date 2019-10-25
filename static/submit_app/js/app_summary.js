var tooltip1 = "Bundle Name is a short, user-friendly name for your App. App Store and IGB App Manager displayBundle Name to users.See <a href='" + getDocLink() + "' target='_blank'>developer’s documentation</a>";
var tooltip2 = "Bundle-SymbolicName and Bundle-Version uniquely identify an IGB App jar file within the IGB OSGi runtime. IGB needs Bundle-Version and Bundle-Symbolic Name to install and run your App. Users never see Bundle-SymbolicName, but IGB needs it to run your App. See <a href='" + getDocLink() + "' target='_blank'>developer’s documentation</a>";
var tooltip3 = "Bundle-Version and Bundle-SymbolicName uniquely identify an IGB App jar file within the IGB OSGi runtime. IGB needs Bundle-Version and Bundle-Symbolic Name to install and run your App. Bundle-Version contain number and full-stop characters only, such as 0.0.1 or 6.1.0. See <a href='" + getDocLink() + "' target='_blank'>developer’s documentation</a>";

document.getElementById("tooltip-1").title= tooltip1;
document.getElementById("tooltip-2").title= tooltip2;
document.getElementById("tooltip-3").title= tooltip3;

$(function() {
    $('form').submit(function() {
        $('input[type=submit]').hide();
        $('#loading').show();
    });
});