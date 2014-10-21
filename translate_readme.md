## i18n Translation steps

i18N translation is implemented using flask babel. The various translation steps are explained below.

#### 1. Give proper permission for translate.sh file

    chmod +x translate.sh


#### 2. Extract Messages and generate pot file

    ./translate.sh -e

#### 3. Generate new language file

    ./translate.sh -g <locale>

For Example

    ./translate.sh -g en_US

Now edit the `translations/en_US/LC_MESSAGES/messages.po` file as needed.

#### 4. Compile translated files

    ./translate.sh -c <translation_directory>

If you come across fuzzy exceptions, remove the fuzzy flag before compiling.

#### 5. Update translated files

    ./translate.sh -u <translation_directory>

#### 6. Practical example

##### a) Extract messages and make translation file for en_us

    ./translate.sh -eg en_US

##### b)Edit the translation files and then execute

    ./translate.sh -c translations

##### c) Update after some strings has changed

    ./translate.sh -eu

Edit the translation files and then execute

    ./translate.sh -c translations


Note: As per flask babel, the translation will happen only if we provide the "msgstr" in the translations/language_code/LC_MESSAGES/messages.po file. If we keep the "msgstr" blank for a particular message, it will render the original english message given.
