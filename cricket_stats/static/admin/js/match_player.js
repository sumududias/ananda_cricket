(function($) {
    $(document).ready(function() {
        // Function to handle the "Add another Match player" button clicks
        function handleAddMatchPlayer() {
            $('.add-row a').click(function(e) {
                e.preventDefault();
                var inningsType = $(this).data('innings-type');
                var totalForms = $('#id_matchplayer_set-TOTAL_FORMS');
                var formCount = parseInt(totalForms.val());
                
                // Clone the empty form template
                var newForm = $('.empty-form.matchplayer_set').clone(true);
                
                // Update form index
                newForm.removeClass('empty-form');
                newForm.html(newForm.html().replace(/__prefix__/g, formCount));
                
                // Set the innings number based on the button clicked
                var inningsSelect = newForm.find('select[id$="-innings_number"]');
                if (inningsType === 'first') {
                    inningsSelect.val('1');
                } else if (inningsType === 'second') {
                    inningsSelect.val('2');
                } else if (inningsType === 'substitute') {
                    inningsSelect.val('0');
                }
                
                // Increment the form count
                totalForms.val(formCount + 1);
                
                // Add the new form to the appropriate section
                var targetSection = $('.innings-' + inningsType);
                if (targetSection.length) {
                    targetSection.append(newForm);
                } else {
                    // Fallback to default location if section not found
                    $('.inline-group').append(newForm);
                }
            });
        }

        // Initialize the handlers
        handleAddMatchPlayer();
    });
})(django.jQuery);
