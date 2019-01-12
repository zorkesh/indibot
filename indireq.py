"""
Indicator requests list
"""

search = 'https://indicator.bifit.ru/api/v2/business-entities/actual'
company_card = search + '/{0}'
markers = company_card + '/analytics/markers'
payment_details = company_card + '/payment-details'
registries = company_card + '/registries-membership'
contacts = company_card + '/contacts'
invalid_confidants = company_card + '/invalid-confidants'
trademarks = company_card + '/trademarks'
proceedings = company_card + '/proceedings'
arbitrations = company_card + '/arbitration-cases'
contracts = company_card + '/contracts'
inspections = company_card + '/inspections'
licenses = company_card + '/licenses'
finance_summary = company_card + '/summary/finance'