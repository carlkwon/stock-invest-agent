# S&P500·나스닥100, 최근 20년 월별 수익률 계절성 분석 (2006-2025, +2026 YTD)

2006~2025년 20년간의 월별 데이터를 직접 집계해 계절성 패턴(승률·평균 수익률)을 검증하고, 같은 기간 나스닥100·미국 장기채(TLT)·미국 단기채(SHY)·금(Gold)과의 연도별 성과를 비교했다. 2026년은 8월 말까지의 YTD(진행중) 수치를 별도로 표시했다.

## 요약

| 구분 | 수치 | 비고 |
|---|---|---|
| S&P500 20년 연평균 | <span style="color:red">12.5%</span> | 단순 평균, 2006-2025 |
| 나스닥100 20년 연평균 | <span style="color:red">18.4%</span> | 단순 평균, 배당 포함 |
| 상승한 해의 비율 | 17/20년 | 하락은 2008·2018·2022년뿐 |
| 최악의 해(주식) | 2008년 | S&P <span style="color:white">-37.0%</span> · 나스닥100 <span style="color:white">-41.7%</span> |
| 미국 장기채(TLT) 20년 연평균 | <span style="color:red">+4.3%</span> | 단순 평균, 배당 포함(토탈리턴). 변동성이 매우 커 연도별 편차가 큼 |
| 최악의 해(장기채) | 2022년 | TLT <span style="color:white">-31.2%</span> (금리 급등기) |
| 금(Gold) 20년 연평균 | <span style="color:red">+12.3%</span> | 단순 평균. 2025년 급등(+63.7%)이 평균을 크게 견인 |
| 최악의 해(금) | 2013년 | 금 <span style="color:white">-28.3%</span> |
| 미국 단기채(SHY) 20년 연평균 | <span style="color:red">+2.0%</span> | 단순 평균, 배당 포함(토탈리턴). 1~3년물로 장기채 대비 변동성이 훨씬 작음 |
| 최악의 해(단기채) | 2022년 | SHY <span style="color:white">-3.9%</span> (장기채 -31.2% 대비 낙폭 미미) |

## 1. 연도별 수익률 비교: S&P500 vs 나스닥100 vs 미국 장기채(TLT) vs 미국 단기채(SHY) vs 금(Gold)

20년 중 두 지수(S&P500·나스닥100) 모두 하락한 해는 2008·2018·2022년 단 3번뿐이었다. 나스닥100은 상승기에 더 크게 오르고 하락기에 더 크게 빠지는, S&P500 대비 높은 변동성(베타)을 20년 내내 일관되게 보였다. 미국 장기채(TLT)는 주식과 반대로 움직이는 전통적 분산 자산이지만, 2022년에는 금리 급등으로 주식(-18.1%)과 장기채(-31.2%)가 **동시에 급락**하는 이례적인 해였다 — 이른바 "60/40 포트폴리오의 악몽"으로 불리는 구간이다. 반면 미국 단기채(SHY, 1~3년물)는 같은 2022년에도 -3.9%에 그쳐, 장기채 대비 금리 변동에 훨씬 덜 민감한 "현금성 자산"에 가까운 안정성을 보였다 — 다만 그만큼 20년 평균 수익률(+2.0%)도 장기채(+4.3%)나 주식에 비해 낮다. 금(Gold)은 주식·채권과 상관관계가 낮은 편이나, 2013년 테이퍼 탠트럼 당시에는 주식이 오르는 와중에도 -28.3% 급락하는 등 절대적인 안전자산은 아니다.

| 연도 | S&P500 | 나스닥100 | 미국 장기채(TLT) | 미국 단기채(SHY) | 금(Gold) |
|---|---|---|---|---|---|
| 2006 | <span style="color:red">+15.8%</span> | <span style="color:red">+7.1%</span> | <span style="color:red">+0.7%</span> | <span style="color:red">+3.9%</span> | <span style="color:red">+22.5%</span> |
| 2007 | <span style="color:red">+5.5%</span> | <span style="color:red">+19.0%</span> | <span style="color:red">+10.3%</span> | <span style="color:red">+7.3%</span> | <span style="color:red">+30.5%</span> |
| 2008 | <span style="color:white">-37.0%</span> | <span style="color:white">-41.7%</span> | <span style="color:red">+33.9%</span> | <span style="color:red">+6.6%</span> | <span style="color:red">+4.9%</span> |
| 2009 | <span style="color:red">+26.5%</span> | <span style="color:red">+54.7%</span> | <span style="color:white">-21.8%</span> | <span style="color:red">+0.3%</span> | <span style="color:red">+24.0%</span> |
| 2010 | <span style="color:red">+15.1%</span> | <span style="color:red">+20.1%</span> | <span style="color:red">+9.1%</span> | <span style="color:red">+2.3%</span> | <span style="color:red">+29.3%</span> |
| 2011 | <span style="color:red">+2.1%</span> | <span style="color:red">+3.5%</span> | <span style="color:red">+34.0%</span> | <span style="color:red">+1.4%</span> | <span style="color:red">+9.6%</span> |
| 2012 | <span style="color:red">+16.0%</span> | <span style="color:red">+18.1%</span> | <span style="color:red">+2.6%</span> | <span style="color:red">+0.3%</span> | <span style="color:red">+6.6%</span> |
| 2013 | <span style="color:red">+32.4%</span> | <span style="color:red">+36.6%</span> | <span style="color:white">-13.4%</span> | <span style="color:red">+0.2%</span> | <span style="color:white">-28.3%</span> |
| 2014 | <span style="color:red">+13.7%</span> | <span style="color:red">+19.2%</span> | <span style="color:red">+27.3%</span> | <span style="color:red">+0.5%</span> | <span style="color:white">-2.2%</span> |
| 2015 | <span style="color:red">+1.4%</span> | <span style="color:red">+9.5%</span> | <span style="color:white">-1.8%</span> | <span style="color:red">+0.4%</span> | <span style="color:white">-10.7%</span> |
| 2016 | <span style="color:red">+12.0%</span> | <span style="color:red">+7.1%</span> | <span style="color:red">+1.2%</span> | <span style="color:red">+0.8%</span> | <span style="color:red">+8.0%</span> |
| 2017 | <span style="color:red">+21.8%</span> | <span style="color:red">+32.7%</span> | <span style="color:red">+9.2%</span> | <span style="color:red">+0.3%</span> | <span style="color:red">+12.8%</span> |
| 2018 | <span style="color:white">-4.4%</span> | <span style="color:white">-0.1%</span> | <span style="color:white">-1.6%</span> | <span style="color:red">+1.5%</span> | <span style="color:white">-1.9%</span> |
| 2019 | <span style="color:red">+31.5%</span> | <span style="color:red">+39.0%</span> | <span style="color:red">+14.1%</span> | <span style="color:red">+3.4%</span> | <span style="color:red">+17.9%</span> |
| 2020 | <span style="color:red">+18.4%</span> | <span style="color:red">+48.4%</span> | <span style="color:red">+18.1%</span> | <span style="color:red">+3.0%</span> | <span style="color:red">+24.8%</span> |
| 2021 | <span style="color:red">+28.7%</span> | <span style="color:red">+27.4%</span> | <span style="color:white">-4.6%</span> | <span style="color:white">-0.7%</span> | <span style="color:white">-4.1%</span> |
| 2022 | <span style="color:white">-18.1%</span> | <span style="color:white">-32.5%</span> | <span style="color:white">-31.2%</span> | <span style="color:white">-3.9%</span> | <span style="color:white">-0.8%</span> |
| 2023 | <span style="color:red">+26.3%</span> | <span style="color:red">+53.8%</span> | <span style="color:red">+2.8%</span> | <span style="color:red">+4.2%</span> | <span style="color:red">+12.7%</span> |
| 2024 | <span style="color:red">+25.0%</span> | <span style="color:red">+25.9%</span> | <span style="color:white">-8.1%</span> | <span style="color:red">+3.9%</span> | <span style="color:red">+26.7%</span> |
| 2025 | <span style="color:red">+17.9%</span> | <span style="color:red">+21.0%</span> | <span style="color:red">+4.3%</span> | <span style="color:red">+5.0%</span> | <span style="color:red">+63.7%</span> |
| **2026(YTD, 8/28 기준)** | <span style="color:red">+13.7%</span> | <span style="color:red">+16.1%</span> | <span style="color:white">-2.4%</span> | <span style="color:red">+0.9%</span> | <span style="color:red">+3.2%</span> |

## 2. S&P500 월별 수익률 히트맵 (2006-2025, +2026 YTD)

| 연도 | 1월 | 2월 | 3월 | 4월 | 5월 | 6월 | 7월 | 8월 | 9월 | 10월 | 11월 | 12월 | 연간 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2006 | <span style="color:red">2.5</span> | <span style="color:red">0.2</span> | <span style="color:red">1.2</span> | <span style="color:red">1.4</span> | <span style="color:white">-3.1</span> | <span style="color:white">-0.1</span> | <span style="color:red">0.5</span> | <span style="color:red">2.1</span> | <span style="color:red">2.4</span> | <span style="color:red">3.2</span> | <span style="color:red">1.7</span> | <span style="color:red">1.4</span> | <span style="color:red">+15.8%</span> |
| 2007 | <span style="color:red">1.4</span> | <span style="color:white">-2.2</span> | <span style="color:red">1.0</span> | <span style="color:red">4.3</span> | <span style="color:red">3.3</span> | <span style="color:white">-1.7</span> | <span style="color:white">-3.2</span> | <span style="color:red">1.3</span> | <span style="color:red">3.6</span> | <span style="color:red">1.5</span> | <span style="color:white">-4.4</span> | <span style="color:white">-0.9</span> | <span style="color:red">+5.5%</span> |
| 2008 | <span style="color:white">-6.1</span> | <span style="color:white">-3.5</span> | <span style="color:white">-0.8</span> | <span style="color:red">4.9</span> | <span style="color:red">1.3</span> | <span style="color:white">-8.6</span> | <span style="color:white">-1.0</span> | <span style="color:red">1.4</span> | <span style="color:white">-9.1</span> | <span style="color:white">-16.9</span> | <span style="color:white">-7.5</span> | <span style="color:red">0.8</span> | <span style="color:white">-37.0%</span> |
| 2009 | <span style="color:white">-8.6</span> | <span style="color:white">-11.0</span> | <span style="color:red">8.5</span> | <span style="color:red">9.4</span> | <span style="color:red">5.3</span> | <span style="color:red">0.2</span> | <span style="color:red">7.5</span> | <span style="color:red">3.6</span> | <span style="color:red">3.7</span> | <span style="color:white">-1.9</span> | <span style="color:red">5.7</span> | <span style="color:red">1.9</span> | <span style="color:red">+26.5%</span> |
| 2010 | <span style="color:white">-3.7</span> | <span style="color:red">2.9</span> | <span style="color:red">5.9</span> | <span style="color:red">1.5</span> | <span style="color:white">-8.2</span> | <span style="color:white">-5.4</span> | <span style="color:red">6.9</span> | <span style="color:white">-4.7</span> | <span style="color:red">8.8</span> | <span style="color:red">3.7</span> | <span style="color:white">-0.2</span> | <span style="color:red">6.7</span> | <span style="color:red">+15.1%</span> |
| 2011 | <span style="color:red">2.3</span> | <span style="color:red">3.2</span> | <span style="color:white">-0.1</span> | <span style="color:red">2.9</span> | <span style="color:white">-1.1</span> | <span style="color:white">-1.8</span> | <span style="color:white">-2.1</span> | <span style="color:white">-5.7</span> | <span style="color:white">-7.2</span> | <span style="color:red">10.8</span> | <span style="color:white">-0.5</span> | <span style="color:red">0.9</span> | <span style="color:red">+2.1%</span> |
| 2012 | <span style="color:red">4.4</span> | <span style="color:red">4.1</span> | <span style="color:red">3.1</span> | <span style="color:white">-0.8</span> | <span style="color:white">-6.3</span> | <span style="color:red">4.0</span> | <span style="color:red">1.3</span> | <span style="color:red">2.0</span> | <span style="color:red">2.4</span> | <span style="color:white">-2.0</span> | <span style="color:red">0.6</span> | <span style="color:red">0.7</span> | <span style="color:red">+16.0%</span> |
| 2013 | <span style="color:red">5.0</span> | <span style="color:red">1.1</span> | <span style="color:red">3.6</span> | <span style="color:red">1.8</span> | <span style="color:red">2.1</span> | <span style="color:white">-1.5</span> | <span style="color:red">5.0</span> | <span style="color:white">-3.1</span> | <span style="color:red">3.0</span> | <span style="color:red">4.5</span> | <span style="color:red">3.0</span> | <span style="color:red">2.4</span> | <span style="color:red">+32.4%</span> |
| 2014 | <span style="color:white">-3.6</span> | <span style="color:red">4.3</span> | <span style="color:red">0.7</span> | <span style="color:red">0.6</span> | <span style="color:red">2.1</span> | <span style="color:red">1.9</span> | <span style="color:white">-1.5</span> | <span style="color:red">3.8</span> | <span style="color:white">-1.6</span> | <span style="color:red">2.3</span> | <span style="color:red">2.5</span> | <span style="color:white">-0.4</span> | <span style="color:red">+13.7%</span> |
| 2015 | <span style="color:white">-3.1</span> | <span style="color:red">5.5</span> | <span style="color:white">-1.7</span> | <span style="color:red">0.9</span> | <span style="color:red">1.1</span> | <span style="color:white">-2.1</span> | <span style="color:red">2.0</span> | <span style="color:white">-6.3</span> | <span style="color:white">-2.6</span> | <span style="color:red">8.3</span> | <span style="color:red">0.3</span> | <span style="color:white">-1.8</span> | <span style="color:red">+1.4%</span> |
| 2016 | <span style="color:white">-5.1</span> | <span style="color:white">-0.4</span> | <span style="color:red">6.6</span> | <span style="color:red">0.3</span> | <span style="color:red">1.5</span> | <span style="color:white">-0.1</span> | <span style="color:red">3.6</span> | <span style="color:red">0.1</span> | <span style="color:red">0.2</span> | <span style="color:white">-1.9</span> | <span style="color:red">3.4</span> | <span style="color:red">1.8</span> | <span style="color:red">+12.0%</span> |
| 2017 | <span style="color:red">1.8</span> | <span style="color:red">3.7</span> | 0.0 | <span style="color:red">0.9</span> | <span style="color:red">1.4</span> | <span style="color:red">0.5</span> | <span style="color:red">1.9</span> | <span style="color:red">0.1</span> | <span style="color:red">1.9</span> | <span style="color:red">2.2</span> | <span style="color:red">2.8</span> | <span style="color:red">1.0</span> | <span style="color:red">+21.8%</span> |
| 2018 | <span style="color:red">5.6</span> | <span style="color:white">-3.9</span> | <span style="color:white">-2.7</span> | <span style="color:red">0.6</span> | <span style="color:red">2.2</span> | <span style="color:red">0.5</span> | <span style="color:red">3.6</span> | <span style="color:red">3.0</span> | <span style="color:red">0.4</span> | <span style="color:white">-6.9</span> | <span style="color:red">1.8</span> | <span style="color:white">-9.2</span> | <span style="color:white">-4.4%</span> |
| 2019 | <span style="color:red">7.9</span> | <span style="color:red">3.0</span> | <span style="color:red">1.8</span> | <span style="color:red">3.9</span> | <span style="color:white">-6.6</span> | <span style="color:red">6.9</span> | <span style="color:red">1.3</span> | <span style="color:white">-1.8</span> | <span style="color:red">1.7</span> | <span style="color:red">2.0</span> | <span style="color:red">3.4</span> | <span style="color:red">2.9</span> | <span style="color:red">+31.5%</span> |
| 2020 | <span style="color:white">-0.2</span> | <span style="color:white">-8.4</span> | <span style="color:white">-12.5</span> | <span style="color:red">12.7</span> | <span style="color:red">4.8</span> | <span style="color:red">1.8</span> | <span style="color:red">5.5</span> | <span style="color:red">7.0</span> | <span style="color:white">-3.9</span> | <span style="color:white">-2.8</span> | <span style="color:red">10.8</span> | <span style="color:red">3.7</span> | <span style="color:red">+18.4%</span> |
| 2021 | <span style="color:white">-1.1</span> | <span style="color:red">2.6</span> | <span style="color:red">4.2</span> | <span style="color:red">5.2</span> | <span style="color:red">0.5</span> | <span style="color:red">2.2</span> | <span style="color:red">2.3</span> | <span style="color:red">2.9</span> | <span style="color:white">-4.8</span> | <span style="color:red">6.9</span> | <span style="color:white">-0.8</span> | <span style="color:red">4.4</span> | <span style="color:red">+28.7%</span> |
| 2022 | <span style="color:white">-5.3</span> | <span style="color:white">-3.1</span> | <span style="color:red">3.7</span> | <span style="color:white">-8.8</span> | 0.0 | <span style="color:white">-8.4</span> | <span style="color:red">9.1</span> | <span style="color:white">-4.2</span> | <span style="color:white">-9.3</span> | <span style="color:red">8.0</span> | <span style="color:red">5.4</span> | <span style="color:white">-5.9</span> | <span style="color:white">-18.1%</span> |
| 2023 | <span style="color:red">6.2</span> | <span style="color:white">-2.6</span> | <span style="color:red">3.5</span> | <span style="color:red">1.5</span> | <span style="color:red">0.3</span> | <span style="color:red">6.5</span> | <span style="color:red">3.1</span> | <span style="color:white">-1.6</span> | <span style="color:white">-4.9</span> | <span style="color:white">-2.2</span> | <span style="color:red">8.9</span> | <span style="color:red">4.4</span> | <span style="color:red">+26.3%</span> |
| 2024 | <span style="color:red">1.6</span> | <span style="color:red">5.2</span> | <span style="color:red">3.1</span> | <span style="color:white">-4.2</span> | <span style="color:red">4.8</span> | <span style="color:red">3.5</span> | <span style="color:red">1.2</span> | <span style="color:red">2.3</span> | <span style="color:red">2.0</span> | <span style="color:white">-1.0</span> | <span style="color:red">5.7</span> | <span style="color:white">-2.5</span> | <span style="color:red">+25.0%</span> |
| 2025 | <span style="color:red">2.7</span> | <span style="color:red">2.5</span> | <span style="color:white">-1.4</span> | <span style="color:red">1.3</span> | <span style="color:red">4.1</span> | <span style="color:red">2.0</span> | <span style="color:red">1.5</span> | <span style="color:red">1.9</span> | <span style="color:white">-1.1</span> | <span style="color:red">2.3</span> | <span style="color:red">0.5</span> | <span style="color:white">-0.5</span> | <span style="color:red">+17.9%</span> |
| **2026\*** | <span style="color:red">1.5</span> | <span style="color:white">-0.9</span> | <span style="color:white">-4.9</span> | <span style="color:red">10.5</span> | <span style="color:red">5.3</span> | <span style="color:white">-1.0</span> | <span style="color:red">0.1</span> | <span style="color:red">3.0</span> | - | - | - | - | <span style="color:red">+13.7%</span>\* |

*\* 2026년은 8월 말까지의 진행중(YTD) 수치이며, 9~12월은 아직 발생하지 않아 "-"로 표기했다. 연간 열의 +13.7%는 최종 연간 수익률이 아니라 8월 말 기준 YTD 값이다.*

## 3. 월별 통계 요약 (S&P500, 20년 실측치 기반 직접 집계)

사용자가 제시한 정성적 계절성 표를 실제 20년치 월별 데이터로 재검증한 결과다. 평균 수익률과 승률(20년 중 상승한 해의 비율)을 함께 표시했다. **아래 통계는 온전한 달력 연도(2006-2025)만을 기준으로 하며, 진행중인 2026년 YTD 수치는 포함하지 않았다** — 아직 발생하지 않은 9~12월 데이터가 없어 연도를 섞으면 월별 평균이 왜곡되기 때문이다.

| 월 | 평균 수익률 | 승률(20년 중) | 특징 |
|---|---|---|---|
| 1월 | <span style="color:red">+0.2%</span> | 55% | 연초 자금 유입과 차익실현이 교차하는 구간 |
| 2월 | <span style="color:red">+0.2%</span> | 60% | 20개월 중 상승 12회로 승률은 준수하나 평균 수익률은 낮은 편 |
| 3월 | <span style="color:red">+1.4%</span> | 65% | 1분기 실적 기대감 반영, 승률·평균 모두 견조 |
| 4월 | <span style="color:red">+2.0%</span> | 85% | 20년 중 최고 평균 수익률(<span style="color:red">+2.0%</span>) 중 하나, 승률도 85%로 전월 대비 최고 |
| 5월 | <span style="color:red">+0.5%</span> | 70% | "Sell in May" 통념과 달리 5월 자체 성과는 나쁘지 않음(승률 70%) |
| 6월 | <span style="color:red">+0.0%</span> | 55% | 평균 수익률이 0%에 가장 근접, 방향성 부재 구간 |
| 7월 | <span style="color:red">+2.4%</span> | 80% | 이번 20년 데이터에서는 평균 수익률이 가장 높은 달(<span style="color:red">+2.4%</span>), 승률도 80%로 상위권 |
| 8월 | <span style="color:red">+0.2%</span> | 65% | 평균은 낮지만 큰 폭의 등락(<span style="color:white">-6.3%</span>~<span style="color:red">+7.0%</span>)이 반복되는 변동성 확대 구간 |
| 9월 | <span style="color:white">-0.7%</span> | 55% | 20년 평균 <span style="color:white">-0.7%</span>로 12개월 중 유일하게 마이너스, "9월 효과" 확인됨 |
| 10월 | <span style="color:red">+1.0%</span> | 60% | 저점 매수세 유입과 급락 사례(2008년 <span style="color:white">-16.9%</span>)가 공존 |
| 11월 | <span style="color:red">+2.2%</span> | 75% | 평균 수익률 <span style="color:red">+2.2%</span>로 상위권, 승률도 75%로 연중 최고 수준 |
| 12월 | <span style="color:red">+0.6%</span> | 65% | 연말 랠리 경향은 있으나 2018·2022년처럼 급락한 해도 존재 |

## 4. 핵심 인사이트

1. **4월과 7월이 20년 평균 최고 수익률 구간이다** — 통념상 "4월·11월이 최강"으로 알려져 있지만, 실제 20년 데이터를 집계하면 7월(<span style="color:red">+2.4%</span>)이 4월(<span style="color:red">+2.0%</span>)과 함께 가장 높은 평균 수익률을 기록했다. 11월(<span style="color:red">+2.2%</span>)도 상위권이지만 1위는 아니었다.

2. **9월 효과는 뚜렷하게 확인된다** — 9월은 12개월 중 유일하게 20년 평균이 마이너스(<span style="color:white">-0.7%</span>)였다. 2008·2011·2022·2023·2025년 등 큰 폭의 하락이 반복되며 "가장 약한 달"이라는 통념이 실제 데이터로도 확인된다.

3. **"Sell in May"는 5월 자체보다 5~10월 구간 전체의 이야기다** — 5월 한 달만 보면 평균 <span style="color:red">+0.5%</span>, 승률 70%로 나쁘지 않다. 다만 6월(0.0%)과 9월(<span style="color:white">-0.7%</span>)이 이 구간에 끼어 있어, 11~4월 대비 5~10월 전체 누적 성과가 상대적으로 약한 것이 "Sell in May" 통념의 실체에 가깝다.

4. **나스닥100은 같은 해에 같이 오르고 같이 내렸다** — 20년 중 나스닥100이 S&P500과 다른 방향으로 움직인 해는 없었다(하락 3개년 2008·2018·2022 완전 일치). 다만 진폭은 항상 더 커서, 2009년 <span style="color:red">+54.7%</span>·2022년 <span style="color:white">-32.5%</span>처럼 상승·하락 모두 S&P500 대비 1.3배 안팎 증폭되는 경향을 보였다.

5. **계절성은 확률적 경향이지 매년 반복되는 규칙이 아니다** — 4월은 20년 중 17번(85%) 올랐지만 3번은 내렸고, 9월도 평균은 마이너스지만 20년 중 11번(55%)은 상승으로 마감했다. 특정 달에 베팅하기보다, 장기 분산투자 전략 안에서 참고 지표로만 활용하는 것이 통계의 한계를 감안한 접근이다.

## 출처 및 방법론

1. **S&P500 월별·연간 수익률(2006-2025)**: 사용자 제공 데이터(토탈리턴 기준) — 2008년 10월 <span style="color:white">-16.9%</span>, 2020년 3~4월 <span style="color:white">-12.5%</span>/<span style="color:red">+12.7%</span>, 2008·2019·2020·2021·2023년 연간 수익률 등 주요 수치를 공개된 시장 데이터와 대조해 정합성을 확인했습니다.
2. **나스닥100(NDX) 연간 수익률(2006-2025, 배당 포함)**: upmyinterest.com, "Nasdaq-100 Historical Annual Returns"
3. **나스닥의 상대적 변동성(베타) 특성**: 다수의 시장 데이터 제공업체 자료에서 공통적으로 언급되는 일반적 특성
4. **미국 장기채(TLT, iShares 20+ Year Treasury Bond ETF) 연간 수익률(2006-2025, 배당 포함)**: upmyinterest.com, "TLT: Historical Annual Returns" — 2008년 급등(+33.9%, 금융위기 안전자산 선호)·2022년 급락(-31.2%, 금리 급등) 등 잘 알려진 역사적 이벤트와 대조해 정합성을 확인했습니다.
5. **미국 단기채(SHY, iShares 1-3 Year Treasury Bond ETF) 연간 수익률(2006-2025, 배당 포함)**: 여러 시장 데이터 제공업체(포트폴리오 분석 사이트 등) 자료를 종합 — 2022년 낙폭(-3.9%)이 장기채(TLT -31.2%) 대비 훨씬 작다는, 듀레이션 차이에 따른 일반적으로 알려진 특성과 부합함을 확인했습니다.
6. **금(Gold, GLD 기준) 연간 수익률(2006-2026 YTD)**: chartrow.com, "Gold Returns by Year" — 2013년 급락(-28.3%)·2025년 급등(+63.7%) 등이 널리 보도된 사실과 부합함을 확인했습니다.
7. **2026년 YTD(1~8월) 데이터**: chartrow.com·statmuse.com(QQQ 기준)·ytdreturn.com(TLT·SHY 기준)·복수 언론·데이터 제공업체 검색 결과를 종합했습니다. S&P500 YTD(토탈리턴) +13.7%(8/27 기준), 나스닥100(QQQ 토탈리턴) +16.1%(8/26 기준), TLT YTD -2.4%(출처별로 -2.1%~-2.7% 사이 소폭 상이), SHY YTD +0.9%, 금 YTD +3.2%. **2026년 수치는 여러 웹 출처를 교차 검색해 종합한 값으로, 8월 이후 확정 데이터가 아닌 진행중(YTD) 수치이며 출처 간 소수점 단위의 오차가 있을 수 있습니다.**

> **참고**: 월별 통계(3장)와 히트맵(2장)의 평균·승률은 본 리포트에서 제공된 2006~2025년 S&P500 월별 수익률 240개 데이터를 직접 합산·평균해 계산한 값이며, 별도의 외부 검증은 거치지 않았습니다. 나스닥100·TLT·SHY·금은 연간 수익률만 별도 출처로 교차 확인했고, 월별 데이터는 신뢰할 수 있는 원자료를 확보하지 못해 포함하지 않았습니다(단, S&P500과 2026년 YTD는 예외) — 다만 나스닥100은 기술주 비중이 높아 S&P500보다 변동성(베타 약 1.1~1.3배)이 구조적으로 크다는 점은 여러 자료에서 일관되게 확인됩니다. 계절성은 과거 확률적 경향일 뿐 매년 반복되는 규칙이 아니며, 특정 연도의 실제 흐름은 통화정책·거시 이벤트 등 펀더멘털 요인에 의해 계절성 패턴을 얼마든지 벗어날 수 있습니다.