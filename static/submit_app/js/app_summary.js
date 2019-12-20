var tooltip1 = "Bundle-Name is a short, user-friendly name for your App. Appstore and IGB App Manager display Bundle-Name to users. See <a href='" + getDocLink() + "' target='_blank'>developer’s documentation</a>.";
var tooltip2 = "Bundle-SymbolicName identifies an IGB App jar file within the IGB OSGi runtime. Users never see Bundle-SymbolicName, but IGB needs it to install and run your App. See <a href='" + getDocLink() + "' target='_blank'>developer’s documentation</a>.";
var tooltip3 = "Bundle-Version is also used to uniquely identify an IGB App jar file within the IGB OSGi runtime and is needed to install and run your App. Bundle-Version should contain only numeric and full-stop characters, e.g. 0.0.1 or 6.1.0. See <a href='" + getDocLink() + "' target='_blank'>developer’s documentation</a>.";

document.getElementById("tooltip-1").title= tooltip1;
document.getElementById("tooltip-2").title= tooltip2;
document.getElementById("tooltip-3").title= tooltip3;

$(function() {
    $('form').submit(function() {
        $('input[type=submit]').hide();
        $('#loading').show();
    });
});