
# TODO

- Move readme check to diagnosis function

# GitHub Actions
    - How to handle private authentication??
      - gspread (should use the json as a secret)
      - github (should be self contained in the github actions)
      - Can we generate github tokens at the organization level?

# QC
    - Add warnings to a final column in the pandas dataframe

# Webiste
    - What would be useful for the website?

# Automatic firmware generation

    - Generate addresses
    - Masks per relevant adresses
      - Use another *_tag_* in the name of the bitmask to have an extra info.
      - Associate tag to address
        - U8 x U16 ??? does this happen?

    - What would a template file look it?
      - Maybe, for each `Mask` byte(s) (`Mask family`) list the addresses that can use it?
      - The automatically generated firmware would then simply be the iteration through `Mask family` family.