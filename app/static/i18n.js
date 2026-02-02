/**
 * Internationalization (i18n) module for School Info Monitor
 * Supports English and Estonian languages
 */
const I18N = {
    languages: {
        en: { name: 'English', nativeName: 'English' },
        et: { name: 'Estonian', nativeName: 'Eesti' }
    },

    currentLang: 'en',

    translations: {
        en: {
            // Mission clock labels
            breakIn: 'Break in',
            lessonStartsIn: 'Lesson starts in',
            schoolStartsIn: 'School starts in',
            inProgress: 'in progress',
            upcoming: 'upcoming',

            // Loading states
            loadingSchedule: 'Loading schedule...',
            loading: 'Loading...',

            // Bus panel
            noBuses: 'No buses',

            // Transport types
            bus: 'Bus',
            trolley: 'Trolley',
            tram: 'Tram',

            // Day names
            days: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],

            // Period name (for schedule display)
            period: 'Period',

            // Settings page
            settings: 'Settings',
            displaySettings: 'Display Settings',
            general: 'General',
            busArrivals: 'Bus Arrivals',
            newsFeed: 'News Feed',
            colors: 'Colors',
            schedule: 'Schedule',
            language: 'Language',

            // Settings labels
            demoMode: 'Demo Mode',
            demoModeDesc: 'Use fake data for testing',
            showBusPanel: 'Show Bus Panel',
            showBusPanelDesc: 'Display real-time bus arrivals',
            stopId: 'Stop ID',
            displayName: 'Display Name',
            newsUrl: 'News URL',

            // Color labels
            duringLesson: 'During Lesson',
            duringBreak: 'During Break',
            beforeSchool: 'Before School',
            afterSchool: 'After School',

            // Buttons
            saveChanges: 'Save Changes',
            discard: 'Discard',
            backToDisplay: 'Display',

            // Toast messages
            settingsSaved: 'Settings saved',
            failedToLoad: 'Failed to load settings',
            failedToSave: 'Failed to save',

            // Substitutions
            substitutions: 'Substitutions',
            substitutionsEnabled: 'Show Substitutions',
            substitutionsEnabledDesc: 'Display schedule changes panel',
            substitutionsUrl: 'Source URL',
            substitutionsRefresh: 'Refresh Interval (minutes)',
            displayWindows: 'Display Time Windows',
            displayWindowsDesc: 'Panel only shows during these times',
            noSubstitutions: 'No changes today',
            cancelled: 'Cancelled',
            roomChange: 'Room change'
        },
        et: {
            // Mission clock labels
            breakIn: 'Vahetund',
            lessonStartsIn: 'Tund algab',
            schoolStartsIn: 'Kool algab',
            inProgress: 'k\u00e4ib',
            upcoming: 'tulemas',

            // Loading states
            loadingSchedule: 'Laen tunniplaani...',
            loading: 'Laen...',

            // Bus panel
            noBuses: 'Busse pole',

            // Transport types
            bus: 'Buss',
            trolley: 'Troll',
            tram: 'Tramm',

            // Day names
            days: ['P\u00fchap\u00e4ev', 'Esmasp\u00e4ev', 'Teisip\u00e4ev', 'Kolmap\u00e4ev', 'Neljap\u00e4ev', 'Reede', 'Laup\u00e4ev'],

            // Period name (for schedule display)
            period: 'tund',

            // Settings page
            settings: 'Seaded',
            displaySettings: 'Ekraani seaded',
            general: '\u00dcldine',
            busArrivals: 'Busside saabumised',
            newsFeed: 'Uudised',
            colors: 'V\u00e4rvid',
            schedule: 'Tunniplaan',
            language: 'Keel',

            // Settings labels
            demoMode: 'Demo re\u017eiim',
            demoModeDesc: 'Kasuta testandmeid',
            showBusPanel: 'N\u00e4ita busside paneeli',
            showBusPanelDesc: 'Kuva reaalajas busside saabumised',
            stopId: 'Peatuse ID',
            displayName: 'Kuvatav nimi',
            newsUrl: 'Uudiste URL',

            // Color labels
            duringLesson: 'Tunni ajal',
            duringBreak: 'Vahetunni ajal',
            beforeSchool: 'Enne kooli',
            afterSchool: 'P\u00e4rast kooli',

            // Buttons
            saveChanges: 'Salvesta',
            discard: 'T\u00fchista',
            backToDisplay: 'Ekraan',

            // Toast messages
            settingsSaved: 'Seaded salvestatud',
            failedToLoad: 'Seadete laadimine eba\u00f5nnestus',
            failedToSave: 'Salvestamine eba\u00f5nnestus',

            // Substitutions
            substitutions: 'Asendused',
            substitutionsEnabled: 'N\u00e4ita asendusi',
            substitutionsEnabledDesc: 'Kuva tunniplaani muudatuste paneel',
            substitutionsUrl: 'Allika URL',
            substitutionsRefresh: 'V\u00e4rskendamise intervall (minutites)',
            displayWindows: 'Kuvamise ajaaknad',
            displayWindowsDesc: 'Paneel kuvatakse ainult nendel aegadel',
            noSubstitutions: 'T\u00e4na muudatusi pole',
            cancelled: 'T\u00fchistatud',
            roomChange: 'Ruumi vahetus'
        }
    },

    /**
     * Initialize with a language code
     * @param {string} lang - Language code ('en' or 'et')
     */
    init(lang) {
        this.currentLang = this.languages[lang] ? lang : 'en';
    },

    /**
     * Get translation for a key
     * @param {string} key - Translation key
     * @returns {string} Translated string or key if not found
     */
    t(key) {
        return this.translations[this.currentLang][key] ||
               this.translations['en'][key] ||
               key;
    },

    /**
     * Get day name by index (0=Sunday, 6=Saturday)
     * @param {number} dayIndex - Day of week (0-6)
     * @returns {string} Localized day name
     */
    getDayName(dayIndex) {
        return this.translations[this.currentLang].days[dayIndex];
    },

    /**
     * Format period name for display
     * English: "Period 1", Estonian: "1. tund"
     * @param {number} num - Period number (1-8)
     * @returns {string} Formatted period name
     */
    formatPeriod(num) {
        if (this.currentLang === 'et') {
            return `${num}. ${this.t('period')}`;
        }
        return `${this.t('period')} ${num}`;
    },

    /**
     * Get transport type name
     * @param {string} type - Type code ('1'=Tram, '2'=Trolley, '3'=Bus) or name
     * @returns {string} Localized transport type
     */
    getTransportType(type) {
        const typeMap = {
            '1': 'tram',
            '2': 'trolley',
            '3': 'bus',
            'Tram': 'tram',
            'Trolley': 'trolley',
            'Bus': 'bus'
        };
        const key = typeMap[type] || type.toLowerCase();
        return this.t(key) || type;
    }
};

// Export for use in modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = I18N;
}
