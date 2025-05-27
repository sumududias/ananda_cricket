(function($) {
    $(document).ready(function() {
        var formatField = $('#id_match_format');
        var totalForms = $('#id_matchplayer_set-TOTAL_FORMS');
        var maxForms = parseInt($('#id_matchplayer_set-MAX_NUM_FORMS').val());

        function updateSecondInningsVisibility() {
            var format = formatField.val();
            if (format === 'TEST') {
                $('.second-innings-radio, .second-innings-button').show();
                $('.innings-2').show();
            } else {
                $('.second-innings-radio, .second-innings-button').hide();
                $('.innings-2').hide();
                // Set all innings to 1 for ODI/T20
                $('input[name$="-innings"]').val(1);
                // Show first innings filter
                $('input[name="innings_filter"][value="1"]').prop('checked', true).trigger('change');
            }
        }

        function addNewRow(button) {
            var formCount = parseInt(totalForms.val());
            var inningsValue = parseInt($(button).data('innings')) || 1;
            var isSubstitute = $(button).data('type') === 'substitute';
            
            if (formCount < maxForms) {
                // Clone the empty form template
                var template = $('#empty-form tr.empty-form').clone(true);
                template.removeClass('empty-form');
                
                // Update form index
                var newFormIndex = formCount;
                var idRegex = new RegExp('(matchplayer_set-\\d+|__prefix__)', 'g');
                var replacement = 'matchplayer_set-' + newFormIndex;
                
                template.attr('id', 'matchplayer_set-' + newFormIndex);
                
                // Update class and styling based on type
                template.removeClass('innings-1 innings-2 substitute');
                if (isSubstitute) {
                    template.addClass('substitute');
                } else {
                    template.addClass('innings-' + inningsValue);
                }
                
                // Update background color and text
                var bgColor = isSubstitute ? '#e8f5e9' : (inningsValue === 2 ? '#fff3e0' : '#e3f2fd');
                template.find('.field-innings').css('background-color', bgColor);
                template.find('.field-innings span').text(isSubstitute ? 'Sub' : (inningsValue === 2 ? '2nd' : '1st'));
                
                // Update all ids and names in the new form
                template.find(':input').each(function() {
                    var input = $(this);
                    if (input.attr('id')) {
                        input.attr('id', input.attr('id').replace(idRegex, replacement));
                    }
                    if (input.attr('name')) {
                        input.attr('name', input.attr('name').replace(idRegex, replacement));
                    }
                });
                
                // Set innings value and substitute status
                var inningsInput = template.find('input[name$="-innings"]');
                inningsInput.val(inningsValue);
                
                // Set substitute status
                var isSubstituteInput = template.find('input[name$="-is_substitute"]');
                if (isSubstituteInput.length) {
                    isSubstituteInput.prop('checked', isSubstitute);
                }
                
                // Clear any values that might have been cloned
                template.find('input:not([type=hidden])').not(inningsInput).not(isSubstituteInput).val('');
                template.find('select').prop('selectedIndex', 0);
                
                // Add the new form to the table
                $('table tbody').append(template);
                
                // Update total form count
                totalForms.val(formCount + 1);

                // Initialize any Django admin widgets
                if (typeof django !== 'undefined' && typeof django.jQuery !== 'undefined') {
                    django.jQuery(document).trigger('formset:added', [template, 'matchplayer_set']);
                }

                // Apply current innings filter
                var currentFilter = $('input[name="innings_filter"]:checked').val();
                if (currentFilter !== 'all') {
                    if (currentFilter === 'sub') {
                        template.toggle(isSubstitute);
                    } else {
                        template.toggle(!isSubstitute && parseInt(currentFilter) === inningsValue);
                    }
                }
            }
        }

        // Handle "Add Player" button clicks
        $('.add-form-row').on('click', function(e) {
            e.preventDefault();
            addNewRow(this);
        });

        // Update on format change
        formatField.on('change', updateSecondInningsVisibility);

        // Initial update
        updateSecondInningsVisibility();

        // Handle innings filter
        $('input[name="innings_filter"]').on('change', function() {
            var value = $(this).val();
            if (value === 'all') {
                $('.form-row').show();
            } else if (value === 'sub') {
                $('.form-row').hide();
                $('.form-row.substitute').show();
            } else {
                $('.form-row').hide();
                $('.form-row.innings-' + value).show();
            }
        });
    });
})(django.jQuery);
